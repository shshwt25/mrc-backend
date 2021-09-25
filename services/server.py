#!/usr/bin/env python
from pathlib import Path
from falcon_cors import CORS
import falcon
from falcon_multipart.middleware import MultipartMiddleware

from .filesUpload.filesUpload import Resource
from .filesDelete.filesDelete import FileManagement
from .fileView.fileView import FileViewer
from .qnaDownload.qnaDownload import QnADownloader
from .questionGenerator.questionGenerator import QuestionGenerator
from .DBCorpus.DBCorpus import DBCorpusResource, DBCorpusDeleteResource, DBCorpusByUserIdResource
from .DBCorpusFiles.DBCorpusFiles import DBCorpusFilesResource, DBCorpusFilesDeleteResource, DBCorpusFilesByUserIdResource
from .DBQnA.DBQnA import DBQnAResource, DBQnAUpdateResource
from .DBAppRoles.DBAppRoles import DBAppRolesResource, DBAppRolesDeleteResource
from .DBAppRolesCorpus.DBAppRolesCorpus import DBAppRolesCorpusResource, DBGetAllRolesCorpusResource, DBAppRolesCorpusMaintainResource
from .DBAppRolesUsers.DBAppRolesUsers import DBAppRolesUsersMaintainResource, DBAppRolesUsersResource
from .DBUser.DBUser import DBUserResource, DBUserDeleteResource, DBUpdateUserGroupResource, DBUpdateUserPasswordResource
from .predictMrcResponse.predictMrcResponse import PredictMrcResponse
from .predictXLNetResponse.predictXLNetResponse import PredictXLNetResponse
from .login.login import Login

from services import *

print("------------------------------------------------------------------------------------------")
print("----------------------------Server started at port 5011-----------------------------------")
print("------------------------------------------------------------------------------------------")

try:
    unicode
except NameError:
    unicode = str

cors = CORS(allow_all_origins=True, allow_all_methods=True, allow_all_headers=True)

# Routes
APP = falcon.API(middleware=[cors.middleware, MultipartMiddleware()])

# File upload routing
APP.add_route('/file_upload', Resource('./documents/'))
APP.add_route('/file_delete', FileManagement())
APP.add_route('/file_view', FileViewer('./documents/'))
APP.add_route('/qna_csv_download', QnADownloader('./qna_csv/'))

APP.add_route('/question_generator', QuestionGenerator())
APP.add_route('/predict_mrc_response', PredictMrcResponse())
APP.add_route('/predict_xlnet_response', PredictXLNetResponse())

# Database Operations
APP.add_route('/db/insert_Corpus', DBCorpusResource())
APP.add_route('/db/get_Corpus_list', DBCorpusResource())
APP.add_route('/db/delete_Corpus', DBCorpusDeleteResource())
APP.add_route('/db/insert_Corpus_File', DBCorpusFilesResource())
APP.add_route('/db/get_Corpus_File_list', DBCorpusFilesResource())
APP.add_route('/db/delete_Corpus_File', DBCorpusFilesDeleteResource())

APP.add_route('/db/get_Corpus_list_by_userid', DBCorpusByUserIdResource())
APP.add_route('/db/get_Corpus_File_list_by_userid', DBCorpusFilesByUserIdResource())

APP.add_route('/db/get_qna', DBQnAResource())
APP.add_route('/db/insert_qna', DBQnAResource())
APP.add_route('/db/update_qna', DBQnAUpdateResource())

# Database Role Maintenance Operations
APP.add_route('/db/insert_App_Role', DBAppRolesResource())
APP.add_route('/db/get_Roles_list', DBAppRolesResource())
APP.add_route('/db/delete_App_Role', DBAppRolesDeleteResource())
APP.add_route('/db/maintain_App_Role_Corpus', DBAppRolesCorpusMaintainResource())
APP.add_route('/db/get_Corpus_by_Role', DBAppRolesCorpusResource())
APP.add_route('/db/get_all_Corpus_by_Roles', DBGetAllRolesCorpusResource())

# Database User Maintenance Operations
APP.add_route('/db/create_user', DBUserResource())
APP.add_route('/db/get_user_detail', DBUserResource())
APP.add_route('/db/delete_user', DBUserDeleteResource())
APP.add_route('/db/update_user_password', DBUpdateUserPasswordResource())
APP.add_route('/db/update_user_group', DBUpdateUserGroupResource())
APP.add_route('/db/maintain_App_Role_User', DBAppRolesUsersMaintainResource())
APP.add_route('/db/get_roles_for_user_id', DBAppRolesUsersResource())



APP.add_route('/login', Login())
