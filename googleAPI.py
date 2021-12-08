import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools
from typing import Optional
import re, mimetypes

class GoogleAPI:
    '''Google Drive API, Google Docs APIの各種操作を提供するクラス
    ''' 
    def __init__(self, drive_token_path='./auth_keys/drive/token.json', docs_token_path='./auth_keys/docs/token.json',
                drive_credentials_path='./auth_keys/drive/credentials.json', docs_credentials_path='./auth_keys/docs/credentials.json') -> None:
        '''Google Drive API, Google Docs APIの各種操作を提供するクラス

        ------
        Parameters
            drive_token_path: str
                Google Drive APIのアクセストークンファイルへのパス
            docs_token_path: str
                Google Drive APIのアクセストークンファイルへのパス
            drive_credentials_path: str
                Google Drive API OAuth2.0クライアントIDファイルへのパス
            docs_credentials_path: str
                Google Docs API OAuth2.0クライアントIDファイルへのパス

        ------
        Note
            tokenが既に存在するならOAuth2.0クライアントIDは指定する必要なし
        ''' 
        self.drive = self.__driveAuth(drive_token_path, drive_credentials_path)
        self.docs  = self.__docsAuth(docs_token_path, docs_credentials_path)
        self.file_name_pattern = re.compile(r'[\w|\d]+.\w+$')
        self.file_type_pattern = re.compile(r'.\w+$')
        mimetypes.types_map[".gdoc"]   = "application/vnd.google-apps.document"
        mimetypes.types_map[".gsheet"] = "application/vnd.google-apps.spreadsheet"

    def __driveAuth(self, token_path:str, drive_credentials_path:str) -> googleapiclient.discovery.Resource:
        '''Google Driveの認証を通して操作用のオブジェクトを返す

        ------
        Returns
            drive: googleapiclient.discovery.Resource
                Google Driveへの操作を提供するオブジェクト
        '''

        SCOPES = ['https://www.googleapis.com/auth/drive']

        store = file.Storage(token_path)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(drive_credentials_path, SCOPES)
            creds = tools.run_flow(flow, store)
        drive = build('drive', 'v3', http=creds.authorize(Http()))
        return drive
    
    def __docsAuth(self, token_path:str, credentials_path:str) -> googleapiclient.discovery.Resource:
        '''Google Docsの認証を通して操作用のオブジェクトを返す

        ------
        Returns
            docs: googleapiclient.discovery.Resource
                Google Docs APIへの操作を提供するオブジェクト
        '''
        SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
        store = file.Storage(token_path)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(credentials_path, SCOPES)
            creds = tools.run_flow(flow, store)
        docs = build('docs', 'v1', credentials=creds)
        return docs

    def createFolder(self, folder_name: str, parents_id: Optional[str]=None) -> str:
        '''Google Dirve上にFolderを作成する

        ------
        Parameters
            folder_name: str
                作成するフォルダの名前
            parents_id: Optional[str]=None
                親フォルダのId

        ------
        Returns
            folder_id: str
                作成したフォルダのID

        ------
        Note
            デフォルトではフォルダはMyDrive/以下に作成される
        '''
        file_metadata = {
            'name'    : folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if not parents_id is None:
            file_metadata['parents'] = [parents_id]
        folder = self.drive.files().create(body=file_metadata,fields='id').execute()
        return folder.get("id")

    def uploadFile(self, file_name: str, file_path: str, parents_id: Optional[str]=None) -> str:
        '''ファイルをアップロードする

        ------
        Parameters
            file_name: str
                アップロード後のファイルの名前
            file_path: str
                アップロードするファイルのパス
            parents_id: Optional[str]=None
                親フォルダのId

        ------
        Returns
            file_id: str
                アップロードしたファイルのID

        ------
        Note
            デフォルトではファイルはMyDrive/以下にアップロードされる
        '''
        mimetypes_after  = mimetypes.guess_type(file_name)[0]
        mimetypes_before = mimetypes.guess_type(file_path)[0]
        image_name = self.file_name_pattern.search(file_path).group()
        file_metadata = {
            'name'    : image_name,
            "mimeType": mimetypes_after,
        }
        if not parents_id is None:
            file_metadata['parents'] = [parents_id]

        media = MediaFileUpload(file_path, mimetype=mimetypes_before, resumable=True)
        image = self.drive.files().create(body=file_metadata,media_body=media,fields='id').execute()
        return image.get("id")

    def deleteFile(self, file_id: str) -> None:
        '''指定したファイルを削除する

        ------
        Parameters
            file_id: str
                削除するファイルのID
        '''
        self.drive.files().delete(fileId=file_id).execute()

    def readText(self, document_id: str) -> str:
        '''Google Docs中のテキストを読み出す

        ------
        Parameters
            document_id: str
                読み込むドキュメントのID

        ------
        Returns
            text: str
                読み出したテキスト
        '''
        document = self.docs.documents().get(documentId=document_id).execute()

        texts = []
        texts_append = texts.append
        for ele in document["body"]["content"]:
            para = ele.get("paragraph")
            if para is not None:
                para = para.get("elements")[0]
                para = para.get("textRun")
                if para is not None:
                    texts_append(para["content"])
        return "".join(texts)

    def OCR(self, image_path:str) -> str:
        '''画像中のテキストを取り出す
        サポートファイルタイプ: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.pdf`

        ------
        Parameters
            image_path: str
                読み込むファイルのパス

        ------
        Returns
            text: 
                読み出したテキスト
        '''

        file_id = self.uploadFile("a.gdoc", image_path)
        text = self.readText(file_id)
        self.deleteFile(file_id)
        return text

def OCRtest():
    def normalize(text: str) -> str:
        return text.replace("　", "").replace(" ", "").replace("\n", "")

    def errorCount(text_a: str, text_b: str) -> int:
        diff = len(text_a) - len(text_b)
        error = 0
        if diff > 0:
            text_b.append("#"*diff)
            error = diff
        elif diff < 0:
            text_b = text_b[:len(text_a)]
            error = -diff
        for char_a, char_b in zip(text_a, text_b):
            if char_a != char_b:
                error += 1

        return error
    
    googelAPI = GoogleAPI()
    correct = "拙者親方と申すは、御立会の内に御存知の御方も御座りましょうが、" \
                "御江戸を発って二十里上方、相州小田原一色町を御過ぎなされて、青物町を上りへ御出でなさるれば、"\
                "欄干橋虎屋藤右衛門、只今では剃髪致して圓斎と名乗りまする。"

    res = normalize(googelAPI.OCR("./img/puretext.jpg"))
    print(res)
    print(f"puretext error: {errorCount(correct, res)}")

    res = normalize(googelAPI.OCR("./img/blur.jpg"))
    print(res)
    print(f"blur error: {errorCount(correct, res)}")

    res = normalize(googelAPI.OCR("./img/coarse.jpg"))
    print(res)
    print(f"coarse error: {errorCount(correct, res)}")
    
    res = normalize(googelAPI.OCR("./img/puretext.pdf"))
    print(res)
    print(f"pdf error: {errorCount(correct, res)}")

if __name__ == '__main__':
    OCRtest()