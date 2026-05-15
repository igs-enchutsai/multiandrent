---
inclusion: always
---

# 媒體處理規範

## 接收圖片

收到格式：
```
[IMAGE: D:\full\path\to\image.jpg] | 用戶說明
```

### 處理步驟
1. 路徑是絕對路徑，可直接讀取
2. 根據用戶說明理解圖片用途
3. 回覆確認收到

## 接收檔案

收到格式：
```
[FILE: D:\full\path\to\file.ext] (name=filename, size=12345) | 用戶說明
```

### 處理步驟
1. 路徑是絕對路徑，可直接讀取
2. 根據副檔名判斷處理方式
3. 回覆確認收到並說明後續動作

## 發送圖片

```
reply_photo(photo_path="D:/full/path/to/image.png", caption="說明")
```

## 發送檔案

```
reply_document(file_path="D:/full/path/to/file.ext", caption="說明")
```

## 重要規則

- 路徑一律使用絕對路徑
- 不可使用相對路徑（agent CWD 與 daemon CWD 不同）
- caption 和說明必須使用繁體中文
