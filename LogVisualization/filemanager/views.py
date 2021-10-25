from django.http import HttpResponse
import os
import json
from filemanager.utils import metaInfoCreate

# 处理文件上传
def fileUpload(request):
    files = request.FILES.getlist('upload')
    print(files)
    baseDir = os.path.dirname(os.path.abspath(__name__))
    for file_name in files:
        with open(os.path.join(baseDir,'tmp',file_name.name),'wb') as f:
            for chrunk in file_name.chunks():
                f.write(chrunk)
            f.flush()
        print(file_name.name)
        metaInfoCreate(file_name.name)
    return HttpResponse(json.dumps({'code': 200}), content_type="application/json")

# 获取元信息
def getMetaInfo(request):
    baseDir = os.path.dirname(os.path.abspath(__name__))
    metaDir = os.path.join(baseDir, 'tmp', 'meta')
    fileNames = os.listdir(metaDir)
    res = []
    for fileName in fileNames:
        with open(os.path.join(metaDir, fileName)) as f:
            info = json.load(f)
        res.append(info)
    return HttpResponse(json.dumps({'code':200,'data':res}), content_type="application/json")

# 删除文件
def fileDelete(request):
    baseDir = os.path.dirname(os.path.abspath(__name__))
    tmpDir = os.path.join(baseDir, 'tmp')
    metaDir = os.path.join(baseDir, 'tmp', 'meta')
    paramDir = os.path.join(baseDir, 'tmp', 'param')
    delFilename = eval(request.body)['data']
    os.remove(tmpDir + '/' + delFilename)
    os.remove(metaDir + '/' + delFilename)
    os.remove(paramDir + '/' + delFilename)

    return HttpResponse(json.dumps({'code': 200}))
