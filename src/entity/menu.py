def get_menu_items(is_topmost):
    return [
        {'text': '退出', 'action': 'quit'},
        {'text': '取消置顶' if is_topmost else '置顶', 'action': 'toggle_topmost'},
        {'text': '切换状态', 'action': 'switch_status_menu'},
    ]

def get_status_menu_items():
    return [
        {'text': '站立', 'action': 'set_standing'},
        {'text': '闲置', 'action': 'set_idle'},
        {'text': '睡觉', 'action': 'set_sleeping'},  # 添加睡觉状态
    ]