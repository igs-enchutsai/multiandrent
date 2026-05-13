// Package config handles team.yaml loading and validation.
package config

import (
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
)

// ChannelConfig holds Telegram channel settings.
type ChannelConfig struct {
	BotTokenEnv    string `yaml:"bot_token_env"`
	GroupID        int64  `yaml:"group_id"`
	GeneralTopicID int    `yaml:"general_topic_id"`
}

// AccessConfig holds access control settings.
type AccessConfig struct {
	Mode         string  `yaml:"mode"`
	AllowedUsers []int64 `yaml:"allowed_users"`
}

// CostGuardConfig holds cost guard settings.
type CostGuardConfig struct {
	DailyLimitUSD    float64 `yaml:"daily_limit_usd"`
	WarnAtPercentage int     `yaml:"warn_at_percentage"`
	Timezone         string  `yaml:"timezone"`
}

// HangDetectorConfig holds hang detector settings.
type HangDetectorConfig struct {
	Enabled        bool `yaml:"enabled"`
	TimeoutMinutes int  `yaml:"timeout_minutes"`
}

// RestartPolicy holds instance restart policy.
type RestartPolicy struct {
	MaxRetries             int    `yaml:"max_retries"`
	Backoff                string `yaml:"backoff"`
	ResetAfter             int    `yaml:"reset_after"`
	HealthCheckIntervalMs  int    `yaml:"health_check_interval_ms"`
}

// InstanceConfig holds per-instance configuration.
type InstanceConfig struct {
	Name             string        `yaml:"-"`
	WorkingDirectory string        `yaml:"working_directory"`
	Description      string        `yaml:"description"`
	TopicID          *int          `yaml:"topic_id"`
	GeneralTopic     bool          `yaml:"general_topic"`
	Role             string        `yaml:"role"`
	Backend          string        `yaml:"backend"`
	Model            string        `yaml:"model"`
	RestartPolicy    RestartPolicy `yaml:"restart_policy"`
}

// TeamConfig is the top-level team.yaml structure.
type TeamConfig struct {
	Channel      ChannelConfig             `yaml:"channel"`
	Access       AccessConfig              `yaml:"access"`
	Defaults     map[string]interface{}    `yaml:"defaults"`
	Instances    map[string]*InstanceConfig `yaml:"instances"`
	CostGuard    CostGuardConfig           `yaml:"cost_guard"`
	HangDetector HangDetectorConfig        `yaml:"hang_detector"`
	HealthPort   int                       `yaml:"health_port"`
}

// GetHome finds the project root by looking for team.yaml in CWD and parent directories.
func GetHome() string {
	if env := os.Getenv("KIRO_MULTI_AGENT_HOME"); env != "" {
		return env
	}
	cwd, err := os.Getwd()
	if err != nil {
		return "."
	}
	dir := cwd
	for {
		if _, err := os.Stat(filepath.Join(dir, "team.yaml")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
	return cwd
}

// LoadTeamConfig loads and parses team.yaml from the given path or auto-detected location.
func LoadTeamConfig(path string) (*TeamConfig, error) {
	if path == "" {
		path = filepath.Join(GetHome(), "team.yaml")
	}

	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("無法讀取 team.yaml: %w", err)
	}

	cfg := &TeamConfig{
		HealthPort: 8470,
		Channel: ChannelConfig{
			BotTokenEnv:    "TELEGRAM_BOT_TOKEN",
			GeneralTopicID: 1,
		},
		Access: AccessConfig{
			Mode: "locked",
		},
		CostGuard: CostGuardConfig{
			WarnAtPercentage: 80,
			Timezone:         "UTC",
		},
		HangDetector: HangDetectorConfig{
			Enabled:        true,
			TimeoutMinutes: 60,
		},
	}

	if err := yaml.Unmarshal(data, cfg); err != nil {
		return nil, fmt.Errorf("team.yaml 解析錯誤: %w", err)
	}

	// Apply defaults and set instance names
	defaultBackend, _ := cfg.Defaults["backend"].(string)
	defaultModel, _ := cfg.Defaults["model"].(string)

	for name, inst := range cfg.Instances {
		inst.Name = name
		if inst.Backend == "" && defaultBackend != "" {
			inst.Backend = defaultBackend
		}
		if inst.Backend == "" {
			inst.Backend = "kiro-cli"
		}
		if inst.Model == "" && defaultModel != "" {
			inst.Model = defaultModel
		}
		if inst.Role == "" {
			inst.Role = "worker"
		}
		if inst.WorkingDirectory == "" {
			inst.WorkingDirectory = filepath.Join(GetHome(), name)
		}
		if inst.RestartPolicy.MaxRetries == 0 {
			inst.RestartPolicy.MaxRetries = 10
		}
		if inst.RestartPolicy.Backoff == "" {
			inst.RestartPolicy.Backoff = "exponential"
		}
		if inst.RestartPolicy.ResetAfter == 0 {
			inst.RestartPolicy.ResetAfter = 300
		}
		if inst.RestartPolicy.HealthCheckIntervalMs == 0 {
			inst.RestartPolicy.HealthCheckIntervalMs = 30000
		}
	}

	return cfg, nil
}
