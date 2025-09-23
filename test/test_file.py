import asyncio
from src.service import upload_file


async def test_upload_file():
    file_name = "文艺小蓝.jpg"
    with open(file_name, "rb") as f:
        image_data = f.read()
    
    result = await upload_file(2, file_name, image_data)
    # FileResponse(key='tos-cn-i-ik7evvg4ik/e2038a9195514a57ae19597b9b5491b4.jpg', name='晓晓.jpg',
    #              md5='44a39fcafa40ce058b04c461ec3ce1d3', size=9050, type='file', file_review_state=1,
    #              file_parse_state=3, identifier='5ecb19a4-9847-11f0-8c87-4a13a9c8e36c')
    print(f"Upload result: {result}")
    print(f"Key: {result.key}")
    print(f"Name: {result.name}")
    print(f"Type: {result.type}")
    print(f"Option: {result.option}")
    assert True


if __name__ == "__main__":
    asyncio.run(test_upload_file())



# if __name__ == "__main__":
#     print("111")