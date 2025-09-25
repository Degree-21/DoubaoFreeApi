import pytest
from src.service import chat_completion, delete_conversation
from src.model.request import CompletionRequest


# @pytest.mark.asyncio
async def test_api_completions():
    # 创建测试数据
    completion = CompletionRequest(
        prompt="让我的卡通人物有以下的属性：尺寸1：1，顶部需要预留10%为图片底色，人物情绪:狂欢，环境：山顶 ，动作：站着，元素：狗，帮我生产2张图片",
        guest=False,  # 使用游客模式进行测试
        conversation_id=None,  # 新聊天使用"0"
        section_id=None,  # 新聊天为null
        attachments=[
            {
                "key": "tos-cn-i-a9rns2rl98/eb983338e9404a29959def3debf1cfc4.jpg",
                "name": "文艺小蓝.jpg",
                "option": {
                    "height": 284,
                    "width": 284
                },
                "type": "vlm_image",
                "file_review_state": 3,
                "file_parse_state": 3,
                "identifier": "dbaba24a-9851-11f0-aa9f-4a13a9c8e36c"
            }
        ],
        use_auto_cot=False,
        use_deep_think=False
    )

    # 调用聊天补全函数
    text, imgs, conv_id, msg_id, sec_id = await chat_completion(
        prompt=completion.prompt,
        guest=completion.guest,
        conversation_id=completion.conversation_id,
        section_id=completion.section_id,
        attachments=completion.attachments,
        use_auto_cot=completion.use_auto_cot,
        use_deep_think=completion.use_deep_think
    )

    # 验证返回值
    assert text is not None, "返回的文本内容不能为空"
    assert isinstance(text, str), "返回的文本内容必须是字符串类型"
    assert len(text) > 0, "返回的文本内容长度必须大于0"

    assert isinstance(imgs, list), "返回的图片URL列表必须是列表类型"

    assert conv_id is not None, "返回的会话ID不能为空"
    assert isinstance(conv_id, str), "返回的会话ID必须是字符串类型"

    assert msg_id is not None, "返回的消息ID不能为空"
    assert isinstance(msg_id, str), "返回的消息ID必须是字符串类型"

    assert sec_id is not None, "返回的段落ID不能为空"
    assert isinstance(sec_id, str), "返回的段落ID必须是字符串类型"

    # 打印详细结果
    print(f"✅ 基础测试通过")
    print(f"📝 返回文本: {text}")
    print(f"🖼️ 图片URL列表: {imgs}")
    print(f"💬 会话ID: {conv_id}")
    print(f"📨 消息ID: {msg_id}")
    print(f"📑 段落ID: {sec_id}")
    print("-" * 50)


# @pytest.mark.asyncio
# async def test_api_completions_with_attachments():
#     # 测试带附件的聊天补全
#     completion = CompletionRequest(
#         prompt="请分析这个图片",
#         guest=True,
#         conversation_id="0",
#         section_id=None,
#         attachments=[
#             {
#                 "key": "test_image_key",
#                 "name": "test_image.jpg",
#                 "type": "image/jpeg",
#                 "file_review_state": 3,
#                 "file_parse_state": 3,
#                 "identifier": "test_identifier_123"
#             }
#         ],
#         use_auto_cot=False,
#         use_deep_think=False
#     )
#
#     # 调用聊天补全函数
#     text, imgs, conv_id, msg_id, sec_id = await chat_completion(
#         prompt=completion.prompt,
#         guest=completion.guest,
#         conversation_id=completion.conversation_id,
#         section_id=completion.section_id,
#         attachments=completion.attachments,
#         use_auto_cot=completion.use_auto_cot,
#         use_deep_think=completion.use_deep_think
#     )
#
#     # 验证返回值
#     assert text is not None, "返回的文本内容不能为空"
#     assert isinstance(text, str), "返回的文本内容必须是字符串类型"
#     assert conv_id is not None, "返回的会话ID不能为空"
#     assert msg_id is not None, "返回的消息ID不能为空"
#     assert sec_id is not None, "返回的段落ID不能为空"
#
#     # 打印详细结果
#     print(f"✅ 带附件测试通过")
#     print(f"📝 返回文本: {text}")
#     print(f"🖼️ 图片URL列表: {imgs}")
#     print(f"💬 会话ID: {conv_id}")
#     print(f"📨 消息ID: {msg_id}")
#     print(f"📑 段落ID: {sec_id}")
#     print("-" * 50)


# @pytest.mark.asyncio
# async def test_api_completions_with_deep_think():
#     # 测试深度思考模式
#     completion = CompletionRequest(
#         prompt="请详细分析量子计算的发展前景",
#         guest=True,
#         conversation_id="0",
#         section_id=None,
#         attachments=[],
#         use_auto_cot=True,
#         use_deep_think=True
#     )
#
#     # 调用聊天补全函数
#     text, imgs, conv_id, msg_id, sec_id = await chat_completion(
#         prompt=completion.prompt,
#         guest=completion.guest,
#         conversation_id=completion.conversation_id,
#         section_id=completion.section_id,
#         attachments=completion.attachments,
#         use_auto_cot=completion.use_auto_cot,
#         use_deep_think=completion.use_deep_think
#     )
#
#     # 验证返回值
#     assert text is not None, "返回的文本内容不能为空"
#     assert isinstance(text, str), "返回的文本内容必须是字符串类型"
#     assert len(text) > 100, "深度思考模式应该返回更详细的内容"
#
#     # 打印详细结果
#     print(f"✅ 深度思考测试通过")
#     print(f"📝 返回文本: {text}")
#     print(f"🖼️ 图片URL列表: {imgs}")
#     print(f"💬 会话ID: {conv_id}")
#     print(f"📨 消息ID: {msg_id}")
#     print(f"📑 段落ID: {sec_id}")
#     print(f"📊 文本长度: {len(text)}")
#     print("-" * 50)


if __name__ == "__main__":
    import asyncio


    async def run_tests():
        print("🚀 开始执行聊天接口测试")

        try:
            await test_api_completions()
            # await test_api_completions_with_attachments()
            # await test_api_completions_with_deep_think()
            print("✅ 所有测试通过!")
        except Exception as e:
            print(f"❌ 测试失败: {e}")


    asyncio.run(run_tests())
