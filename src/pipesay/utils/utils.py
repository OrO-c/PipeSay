import os
import subprocess


def enter_to_next(prompt: str):
    """
    对程序进行阻塞使用户可以阅读句子/提示信息等再进行下一步
    
    Args:
        prompt(str): 向用户展示的提示信息
    """
    
    input(prompt)

def clear_screen():
    """清理屏幕上原有信息"""
    if os.name == 'nt':
        subprocess.run('cls', shell=True, check=False)
    else:
        subprocess.run('clear', shell=True, check=False)