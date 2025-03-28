import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

def generate_sample_names(first_name, total_rows):
    """生成样品名称"""
    # 提取基础名称和起始数字
    base_name = ''.join(filter(str.isalpha, first_name))
    start_num = int(''.join(filter(str.isdigit, first_name)))
    
    all_names = []
    for row in range(total_rows):
        row_names = []
        for col in range(17):  # 17个电泳孔
            if col == 8:  # 第9个位置
                row_names.append('M')
            else:
                # 计算当前位置的编号
                current_num = start_num + col + (row * 16)  # 16是除去M后每行的数量
                if col > 8:  # 如果在M之后，需要减1以保持连续性
                    current_num -= 1
                row_names.append(f"{base_name}{current_num}")
        all_names.append(row_names)
    return all_names

def draw_labels_on_image(image, sample_names):
    """在图片上绘制标签"""
    img = image.copy()
    height, width = img.shape[:2]
    row_height = height // len(sample_names)
    
    for row_idx, row_names in enumerate(sample_names):
        for col_idx, name in enumerate(row_names):
            # 计算文字位置
            x = int((width * (col_idx + 0.5)) / 17)  # 17等分
            y = int((row_height * (row_idx + 0.5)))
            
            # 添加文字
            cv2.putText(img, name, (x-20, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    return img

def main():
    st.title("电泳图片样品标记工具")
    
    # 文件上传
    uploaded_file = st.file_uploader("上传电泳图片", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        # 读取图片
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # 显示原始图片
        st.image(uploaded_file, caption="原始图片", use_column_width=True)
        
        # 输入参数
        first_name = st.text_input("请输入第一个样品的名称（例如：XM1）：")
        num_rows = st.number_input("请输入行数（1-8）：", min_value=1, max_value=8, value=1)
        
        if first_name and st.button("生成标记"):
            # 生成样品名称
            sample_names = generate_sample_names(first_name, num_rows)
            
            # 在图片上添加标签
            labeled_image = draw_labels_on_image(image, sample_names)
            
            # 显示结果
            st.image(labeled_image, caption="标记后的图片", use_column_width=True)
            
            # 生成Markdown格式的样品名称表格
            st.markdown("### 样品名称表格")
            markdown_table = "| " + " | ".join(["列" + str(i+1) for i in range(17)]) + " |\n"
            markdown_table += "|" + "|".join(["---" for _ in range(17)]) + "|\n"
            
            for row in sample_names:
                markdown_table += "| " + " | ".join(row) + " |\n"
            
            st.markdown(markdown_table)
            
            # 提供下载标记后的图片
            is_success, buffer = cv2.imencode(".png", labeled_image)
            if is_success:
                btn = st.download_button(
                    label="下载标记后的图片",
                    data=buffer.tobytes(),
                    file_name="labeled_gel.png",
                    mime="image/png"
                )

if __name__ == "__main__":
    main()