---
inclusion: always
---

# 媒體處理指南

## 接收圖片

當用戶發送圖片時，你會收到格式如下的訊息：
```
[IMAGE: media/leader-agent/AbCdEf123.jpg]
用戶的文字說明（如果有的話）
```

### 處理步驟
1. 確認圖片路徑存在
2. 根據用戶說明理解圖片用途
3. 如果需要分析圖片內容，說明你看到的（Kiro 支援圖片理解）
4. 回覆用戶確認收到

## 接收檔案

當用戶發送檔案時，你會收到格式如下的訊息：
```
[FILE: media/leader-agent/document.pdf] (name=document.pdf, size=12345)
用戶的文字說明（如果有的話）
```

### 處理步驟
1. 確認檔案路徑和類型
2. 根據副檔名判斷處理方式
3. 如果是程式碼或文字檔，可以讀取內容
4. 回覆用戶確認收到並說明後續動作

## 發送圖片給用戶

```
reply_photo(photo_path="path/to/image.png", caption="圖片說明")
```

### 支援格式
- JPG, PNG, GIF, WebP
- 最大 10MB（Telegram 限制）
- 建議壓縮大圖片再發送

## 發送檔案給用戶

```
reply_document(file_path="path/to/file.ext", caption="檔案說明")
```

### 支援格式
- 任何檔案類型
- 最大 50MB（Telegram 限制）
- 檔名會保留原始名稱

## 媒體目錄結構

```
media/
└── leader-agent/
    ├── AbCdEf123.jpg      # 用戶上傳的圖片
    ├── document.pdf        # 用戶上傳的檔案
    └── ...
```

使用 `list_media_files()` 工具可以列出所有已收到的媒體檔案。
