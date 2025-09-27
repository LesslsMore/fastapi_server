from utils.s3_util import S3Service

s3_service = S3Service()

def test_upload_file():
    s3_service = S3Service()

    file_name = r'E:\30-Interest\6-Animation\test_preview.jpg'
    response = s3_service.upload_file(file_name, {
        'ACL': 'public-read',  # 核心：设置访问控制列表
        'ContentType': 'image/jpeg'  # 建议同时设置正确的ContentType
    })

    print(response)


def test_upload_file_pdf():
    s3_service = S3Service()

    # file_name = r'E:\T\Downloads\Documents\练习三.pdf'
    file_name = r'E:\30-Interest\6-Animation\物语系列短篇集Part A.pdf'
    # file_name = r'E:\30-Interest\6-Animation\物语系列短篇集Part B.pdf'
    response = s3_service.upload_file(file_name, {
        'ACL': 'public-read',  # 核心：设置访问控制列表
        'ContentType': 'application/pdf'  # 核心：设置内容类型为PDF
    })

    res = s3_service.get_static_url(None, file_name)
    print(res)
    print(response)

def test_get_static_url():
    file_name = r'E:\30-Interest\6-Animation\物语系列短篇集Part B.pdf'
    res = s3_service.get_static_url(None, file_name)
    print(res)


def test_put_acl():
    s3_service = S3Service()
    s3_service.put_acl('1.txt')


def test_copy_from():
    s3_service = S3Service()
    s3_service.copy_from('1.txt', "text/plain; charset=utf-8")


def test_copy_object():
    s3_service = S3Service()
    key = 'keyboard-shortcuts-windows.pdf'
    content_type = "application/octet-stream"
    s3_service.copy_object(key, content_type)


def test_upload_fileobj():
    s3_service = S3Service()
    file_name = r'D:\T\Downloads\1.txt'
    s3_service.upload_fileobj(file_name)


def test_generate_presigned_url():
    s3_service = S3Service()
    object_name = 'test_preview.jpg'
    s3_service.generate_presigned_url(object_name)
