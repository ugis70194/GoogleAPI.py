# GoogleAPI.py

## Requirements

[Google Cloud Platform](https://console.cloud.google.com)でプロジェクトを作成し、
[Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com)と
[Google Docs API](https://console.cloud.google.com/apis/library/docs.googleapis.com)を有効化し、OAuth2.0クライアントIDを取得しておいてください。  
OAuth2.0クライアントIDファイルとアクセストークンファイルは、  
Google Drive APIは `./auth_keys/drive/`  
Google Docs APIは `./auth_keys/docs/`  
以下を読みにいくのでそこにファイルを置くか、クラスインスタンス作成時にファイルの場所を指定してください。  
一連の手順については、詳しくやり方を書いて頂いている方がいるので[こちら](https://zenn.dev/wtkn25/articles/python-googledriveapi-auth#google-developer-console%E3%81%AB%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9)を参照してください。  
現在はアプリケーションの種類に`その他`がなくなっています。代わりに`デスクトップアプリケーション`を選択してください

必要なライブラリは
```
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client
```
でインストールできます。

## Example
```py
from googleAPI import GoogleAPI

googleAPI = GoogleAPI(drive_token_path='./auth_keys/drive/token.json', docs_token_path='./auth_keys/docs/token.json',
                drive_credentials_path='./auth_keys/drive/credentials.json', docs_credentials_path='./auth_keys/docs/credentials.json')
print(googleAPI.OCR("./text.jpg"))
```

## Mothods

### \_\_init\_\_(self, drive_token_path, docs_token_path,drive_credentials_path, docs_credentials_path) -> None:
GoogleAPIクラスのコンストラクタ

#### Parameters
- drive_token_path: str
    - Google Drive APIのアクセストークンファイルへのパス
    - default: './auth_keys/drive/token.json'
- docs_token_path: str
    - Google Drive APIのアクセストークンファイルへのパス
    - default: './auth_keys/docs/token.json'
- drive_credentials_path: str
    - Google Drive API OAuth2.0クライアントIDファイルへのパス
    - default: './auth_keys/drive/credentials.json'
- docs_credentials_path: str
    - Google Docs API OAuth2.0クライアントIDファイルへのパス
    - default: './auth_keys/docs/credentials.json'

#### Note
tokenが既に存在するならOAuth2.0クライアントIDは指定する必要なし

### createFolder(self, folder_name: str, parents_id: Optional[str]=None) -> str:
Google Dirve上にFolderを作成する

#### Parameters
- folder_name: str
    - 作成するフォルダの名前
- parents_id: Optional[str]=None
    - 親フォルダのId

#### Returns
- folder_id: str
    -作成したフォルダのID
        
#### Note
デフォルトではフォルダはMyDrive/以下に作成される


### uploadFile(self, file_name: str, file_path: str, parents_id: Optional[str]=None) -> str:
ファイルをアップロードする

#### Parameters
- file_name: str
    - アップロード後のファイルの名前
- file_path: str
    - アップロードするファイルのパス
- parents_id: Optional[str]=None
    - 親フォルダのId

#### Returns
- file_id: str
    - アップロードしたファイルのID

#### Note
デフォルトではファイルはMyDrive/以下にアップロードされる


### deleteFile(self, file_id: str) -> None:
指定したファイルを削除する

#### Parameters
- file_id: str
    - 削除するファイルのID

### readText(self, document_id: str) -> str:
Google Docs中のテキストを読み出す

#### Parameters
- document_id: str
    - 読み込むドキュメントのID

#### Returns
- text: str
    - 読み出したテキスト

### OCR(self, image_path:str) -> str:
画像中のテキストを取り出す
サポートファイルタイプ: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.pdf`
#### Parameters
- image_path: str
    - 読み込む画像のパス

#### Returns
- text: 
    - 読み出したテキスト
