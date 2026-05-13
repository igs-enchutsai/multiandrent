// Package telegram provides the TelegramAdapter for message routing.
package telegram

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"kiro-multi-agent/internal/config"
	"kiro-multi-agent/internal/daemon"
)

const telegramMaxText = 4096

// rawUpdate is used to parse Telegram updates with message_thread_id support.
type rawUpdate struct {
	UpdateID int        `json:"update_id"`
	Message  *rawMessage `json:"message"`
}

type rawMessage struct {
	MessageID       int          `json:"message_id"`
	From            *rawUser     `json:"from"`
	Chat            *rawChat     `json:"chat"`
	MessageThreadID int          `json:"message_thread_id"`
	Text            string       `json:"text"`
	Caption         string       `json:"caption"`
	Photo           []rawPhoto   `json:"photo"`
	Document        *rawDocument `json:"document"`
}

type rawUser struct {
	ID       int64  `json:"id"`
	UserName string `json:"username"`
}

type rawChat struct {
	ID int64 `json:"id"`
}

type rawPhoto struct {
	FileID       string `json:"file_id"`
	FileUniqueID string `json:"file_unique_id"`
	Width        int    `json:"width"`
	Height       int    `json:"height"`
}

type rawDocument struct {
	FileID       string `json:"file_id"`
	FileUniqueID string `json:"file_unique_id"`
	FileName     string `json:"file_name"`
	FileSize     int64  `json:"file_size"`
}

type rawFile struct {
	FileID   string `json:"file_id"`
	FilePath string `json:"file_path"`
}

type rawGetFileResponse struct {
	OK     bool    `json:"ok"`
	Result rawFile `json:"result"`
}

type rawGetUpdatesResponse struct {
	OK     bool        `json:"ok"`
	Result []rawUpdate `json:"result"`
}

// Adapter routes Telegram messages to agent instances based on Forum Topic ID.
type Adapter struct {
	config *config.TeamConfig
	daemon *daemon.Daemon
	token  string

	topicToInstance map[int]string
	instanceToTopic map[string]int
	mediaDir        string

	stopCh chan struct{}
	wg     sync.WaitGroup
}

// New creates a new TelegramAdapter.
func New(cfg *config.TeamConfig, d *daemon.Daemon) *Adapter {
	a := &Adapter{
		config:          cfg,
		daemon:          d,
		topicToInstance:  make(map[int]string),
		instanceToTopic: make(map[string]int),
		mediaDir:        "media",
		stopCh:          make(chan struct{}),
	}
	a.buildRoutingTable()
	return a
}

func (a *Adapter) buildRoutingTable() {
	for name, ic := range a.config.Instances {
		if ic.TopicID != nil {
			a.topicToInstance[*ic.TopicID] = name
			a.instanceToTopic[name] = *ic.TopicID
		}
	}
	log.Printf("[telegram] 路由表: %d 個 topic 已映射", len(a.topicToInstance))
}

func (a *Adapter) isAllowedUser(userID int64) bool {
	if len(a.config.Access.AllowedUsers) == 0 {
		return true
	}
	for _, id := range a.config.Access.AllowedUsers {
		if id == userID {
			return true
		}
	}
	return false
}

func (a *Adapter) resolveInstance(threadID int) string {
	if name, ok := a.topicToInstance[threadID]; ok {
		return name
	}
	// General topic -> find instance with general_topic=true
	for name, ic := range a.config.Instances {
		if ic.GeneralTopic {
			return name
		}
	}
	return ""
}

// Start begins polling for Telegram updates using raw HTTP (to support message_thread_id).
func (a *Adapter) Start() error {
	token := os.Getenv(a.config.Channel.BotTokenEnv)
	if token == "" {
		return fmt.Errorf("Bot token 未設定 (env: %s)", a.config.Channel.BotTokenEnv)
	}
	a.token = token

	os.MkdirAll(a.mediaDir, 0755)

	// Verify bot connection
	botInfo, err := a.apiGet("getMe")
	if err != nil {
		return fmt.Errorf("建立 Telegram Bot 失敗: %w", err)
	}
	var meResult struct {
		OK     bool `json:"ok"`
		Result struct {
			UserName string `json:"username"`
		} `json:"result"`
	}
	json.Unmarshal(botInfo, &meResult)
	log.Printf("[telegram] Bot 已連線: @%s", meResult.Result.UserName)

	a.wg.Add(1)
	go a.pollLoop()

	log.Printf("[telegram] 開始輪詢更新")
	return nil
}

// Stop stops the Telegram bot polling.
func (a *Adapter) Stop() {
	close(a.stopCh)
	a.wg.Wait()
	log.Printf("[telegram] Bot 已停止")
}

func (a *Adapter) pollLoop() {
	defer a.wg.Done()

	offset := 0
	client := &http.Client{Timeout: 65 * time.Second}

	for {
		select {
		case <-a.stopCh:
			return
		default:
		}

		url := fmt.Sprintf("https://api.telegram.org/bot%s/getUpdates?offset=%d&timeout=60&allowed_updates=[\"message\"]",
			a.token, offset)

		resp, err := client.Get(url)
		if err != nil {
			log.Printf("[telegram] 輪詢錯誤: %v", err)
			time.Sleep(5 * time.Second)
			continue
		}

		body, _ := io.ReadAll(resp.Body)
		resp.Body.Close()

		var updates rawGetUpdatesResponse
		if err := json.Unmarshal(body, &updates); err != nil {
			log.Printf("[telegram] 解析更新失敗: %v", err)
			time.Sleep(2 * time.Second)
			continue
		}

		for _, update := range updates.Result {
			offset = update.UpdateID + 1
			a.handleUpdate(update)
		}
	}
}

func (a *Adapter) handleUpdate(update rawUpdate) {
	msg := update.Message
	if msg == nil {
		return
	}

	user := msg.From
	if user == nil || !a.isAllowedUser(user.ID) {
		return
	}

	threadID := msg.MessageThreadID
	instance := a.resolveInstance(threadID)
	if instance == "" {
		return
	}

	// Handle different message types in goroutines (non-blocking)
	if len(msg.Photo) > 0 {
		go a.handlePhoto(instance, msg, user)
	} else if msg.Document != nil {
		go a.handleDocument(instance, msg, user)
	} else if msg.Text != "" {
		go a.handleText(instance, msg, user)
	}
}

func (a *Adapter) handleText(instance string, msg *rawMessage, user *rawUser) {
	text := msg.Text
	log.Printf("[telegram] [text] %s -> %s: %s", user.UserName, instance, truncate(text, 80))

	response, err := a.daemon.SendMessage(instance, text)
	if err != nil {
		log.Printf("[telegram] 發送訊息到 %s 失敗: %v", instance, err)
		return
	}
	if response != "" {
		a.SendText(instance, response)
	} else {
		log.Printf("[telegram] %s 無回應", instance)
	}
}

func (a *Adapter) handlePhoto(instance string, msg *rawMessage, user *rawUser) {
	// Get highest resolution photo
	photo := msg.Photo[len(msg.Photo)-1]

	filePath, err := a.getFilePath(photo.FileID)
	if err != nil {
		log.Printf("[telegram] 取得照片失敗: %v", err)
		return
	}

	// Download to media directory
	instDir := filepath.Join(a.mediaDir, instance)
	os.MkdirAll(instDir, 0755)
	localPath := filepath.Join(instDir, photo.FileUniqueID+".jpg")

	if err := a.downloadFile(filePath, localPath); err != nil {
		log.Printf("[telegram] 下載照片失敗: %v", err)
		return
	}

	caption := msg.Caption
	payload := fmt.Sprintf("[IMAGE: %s]", localPath)
	if caption != "" {
		payload += "\n" + caption
	}

	log.Printf("[telegram] [photo] %s -> %s: %s", user.UserName, instance, localPath)

	response, err := a.daemon.SendMessage(instance, payload)
	if err != nil {
		log.Printf("[telegram] 發送訊息到 %s 失敗: %v", instance, err)
		return
	}
	if response != "" {
		a.SendText(instance, response)
	}
}

func (a *Adapter) handleDocument(instance string, msg *rawMessage, user *rawUser) {
	doc := msg.Document

	filePath, err := a.getFilePath(doc.FileID)
	if err != nil {
		log.Printf("[telegram] 取得文件失敗: %v", err)
		return
	}

	instDir := filepath.Join(a.mediaDir, instance)
	os.MkdirAll(instDir, 0755)
	filename := doc.FileName
	if filename == "" {
		filename = doc.FileUniqueID
	}
	localPath := filepath.Join(instDir, filename)

	if err := a.downloadFile(filePath, localPath); err != nil {
		log.Printf("[telegram] 下載文件失敗: %v", err)
		return
	}

	caption := msg.Caption
	payload := fmt.Sprintf("[FILE: %s] (name=%s, size=%d)", localPath, filename, doc.FileSize)
	if caption != "" {
		payload += "\n" + caption
	}

	log.Printf("[telegram] [doc] %s -> %s: %s", user.UserName, instance, filename)

	response, err := a.daemon.SendMessage(instance, payload)
	if err != nil {
		log.Printf("[telegram] 發送訊息到 %s 失敗: %v", instance, err)
		return
	}
	if response != "" {
		a.SendText(instance, response)
	}
}

func (a *Adapter) getFilePath(fileID string) (string, error) {
	data, err := a.apiGet(fmt.Sprintf("getFile?file_id=%s", fileID))
	if err != nil {
		return "", err
	}
	var result rawGetFileResponse
	if err := json.Unmarshal(data, &result); err != nil {
		return "", err
	}
	if !result.OK {
		return "", fmt.Errorf("getFile failed")
	}
	return result.Result.FilePath, nil
}

func (a *Adapter) downloadFile(filePath string, localPath string) error {
	url := fmt.Sprintf("https://api.telegram.org/file/bot%s/%s", a.token, filePath)

	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	out, err := os.Create(localPath)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	return err
}

// SendText sends text to the Telegram topic for this instance.
// Auto-splits messages longer than 4096 chars.
func (a *Adapter) SendText(instance string, text string) bool {
	if a.token == "" {
		log.Printf("[telegram] Bot 未初始化，無法發送")
		return false
	}

	topicID, hasTopicID := a.instanceToTopic[instance]
	chatID := a.config.Channel.GroupID
	if chatID == 0 {
		return false
	}

	chunks := splitText(text)
	for _, chunk := range chunks {
		params := map[string]interface{}{
			"chat_id": chatID,
			"text":    chunk,
		}
		if hasTopicID {
			params["message_thread_id"] = topicID
		}
		if _, err := a.apiPost("sendMessage", params); err != nil {
			log.Printf("[telegram] 發送文字到 %s 失敗: %v", instance, err)
			return false
		}
	}
	return true
}

// SendPhoto sends a photo to the Telegram topic for this instance.
func (a *Adapter) SendPhoto(instance string, photoPath string, caption string) bool {
	if a.token == "" {
		return false
	}

	topicID, hasTopicID := a.instanceToTopic[instance]
	chatID := a.config.Channel.GroupID
	if chatID == 0 {
		return false
	}

	if _, err := os.Stat(photoPath); os.IsNotExist(err) {
		log.Printf("[telegram] 照片不存在: %s", photoPath)
		return false
	}

	// Use multipart form for file upload
	fields := map[string]string{
		"chat_id": fmt.Sprintf("%d", chatID),
	}
	if hasTopicID {
		fields["message_thread_id"] = fmt.Sprintf("%d", topicID)
	}
	if caption != "" {
		if len(caption) > 1024 {
			caption = caption[:1024]
		}
		fields["caption"] = caption
	}

	if err := a.apiUpload("sendPhoto", "photo", photoPath, fields); err != nil {
		log.Printf("[telegram] 發送照片到 %s 失敗: %v", instance, err)
		return false
	}
	return true
}

// SendDocument sends a document to the Telegram topic for this instance.
func (a *Adapter) SendDocument(instance string, filePath string, caption string) bool {
	if a.token == "" {
		return false
	}

	topicID, hasTopicID := a.instanceToTopic[instance]
	chatID := a.config.Channel.GroupID
	if chatID == 0 {
		return false
	}

	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		log.Printf("[telegram] 文件不存在: %s", filePath)
		return false
	}

	fields := map[string]string{
		"chat_id": fmt.Sprintf("%d", chatID),
	}
	if hasTopicID {
		fields["message_thread_id"] = fmt.Sprintf("%d", topicID)
	}
	if caption != "" {
		if len(caption) > 1024 {
			caption = caption[:1024]
		}
		fields["caption"] = caption
	}

	if err := a.apiUpload("sendDocument", "document", filePath, fields); err != nil {
		log.Printf("[telegram] 發送文件到 %s 失敗: %v", instance, err)
		return false
	}
	return true
}

// ─── Telegram API helpers ───────────────────────────────────────

func (a *Adapter) apiGet(method string) ([]byte, error) {
	url := fmt.Sprintf("https://api.telegram.org/bot%s/%s", a.token, method)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}

func (a *Adapter) apiPost(method string, params map[string]interface{}) ([]byte, error) {
	url := fmt.Sprintf("https://api.telegram.org/bot%s/%s", a.token, method)
	jsonData, _ := json.Marshal(params)
	resp, err := http.Post(url, "application/json", bytes.NewReader(jsonData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}

func (a *Adapter) apiUpload(method string, fileField string, filePath string, fields map[string]string) error {
	url := fmt.Sprintf("https://api.telegram.org/bot%s/%s", a.token, method)

	var buf bytes.Buffer
	writer := multipart.NewWriter(&buf)

	// Add text fields
	for k, v := range fields {
		writer.WriteField(k, v)
	}

	// Add file
	file, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	part, err := writer.CreateFormFile(fileField, filepath.Base(filePath))
	if err != nil {
		return err
	}
	io.Copy(part, file)
	writer.Close()

	resp, err := http.Post(url, writer.FormDataContentType(), &buf)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}
	return nil
}

// ─── Utilities ───────────────────────────────────────────────────

// splitText splits text into chunks of max telegramMaxText chars.
// Tries to split at newlines, then at spaces, then hard-cut.
func splitText(text string) []string {
	if len(text) <= telegramMaxText {
		return []string{text}
	}

	var chunks []string
	remaining := text

	for len(remaining) > 0 {
		if len(remaining) <= telegramMaxText {
			chunks = append(chunks, remaining)
			break
		}

		cut := telegramMaxText
		// Prefer splitting at newline
		nlPos := strings.LastIndex(remaining[:cut], "\n")
		if nlPos > cut/2 {
			cut = nlPos + 1
		} else {
			// Try splitting at space
			spPos := strings.LastIndex(remaining[:cut], " ")
			if spPos > cut/2 {
				cut = spPos + 1
			}
		}

		chunks = append(chunks, remaining[:cut])
		remaining = remaining[cut:]
	}

	return chunks
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "..."
}
