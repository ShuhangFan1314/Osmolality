import streamlit as st
import pandas as pd

# 设置页面配置
st.set_page_config(
    page_title="渗透压计算器",
    page_icon="🧪",
    layout="centered",
)

# 创建数据库
def create_database():
    # 缓冲液组成数据库
    buffer_data = {
        "Buffer": [
            "20mM Acetate,pH 4.5", "20mM Acetate,pH 5.0", "20mM Acetate,pH 5.5", 
            "20mM Citrate,pH 5.0", "20mM Citrate,pH 5.5","20mM Citrate,pH 6.0","20mM Citrate,pH 6.5",
            "20mM Histidine,pH 5.5","20mM Histidine,pH 6.0","20mM Histidine,pH 6.5",
            "20mM Phosphate,pH 6.0", "20mM Phosphate,pH 6.5", "20mM Phosphate,pH 7.0", "20mM Phosphate,pH 7.5"
        ],
        "Osmolality (mOsmol/kg)": [29, 35, 38, 53, 56, 59, 62, 36, 32, 28, 42, 44, 48, 51]
    }
    buffer_df = pd.DataFrame(buffer_data)

    # 辅料数据库
    excipient_data = {
        "Excipient": ["Sucrose", "Sodium Chloride", "Mannitol", "Trehalose", "Arginine Hydrochloride"],
        "Osmolality (mOsmol/kg/mg/mL)": [3.1, 31.3, 5.8, 2.9, 8.1]
    }
    excipient_df = pd.DataFrame(excipient_data)

    return buffer_df, excipient_df

# 计算渗透压
def calculate_Osmolality(buffer_df, excipient_df, buffer_choice, excipient_choices, excipient_concentrations, protein_Osmolality, protein_buffer_choice):
    # 获取缓冲液的渗透压
    buffer_Osmolality_selected = buffer_df[buffer_df["Buffer"] == buffer_choice]["Osmolality (mOsmol/kg)"].values[0]

    # 获取蛋白检测时缓冲液的渗透压
    protein_buffer_Osmolality = buffer_df[buffer_df["Buffer"] == protein_buffer_choice]["Osmolality (mOsmol/kg)"].values[0]

    # 计算辅料的总渗透压
    total_excipient_Osmolality = 0
    for excipient_choice, excipient_concentration in zip(excipient_choices, excipient_concentrations):
        excipient_Osmolality = excipient_df[excipient_df["Excipient"] == excipient_choice]["Osmolality (mOsmol/kg/mg/mL)"].values[0]
        total_excipient_Osmolality += excipient_Osmolality * excipient_concentration

    # 扣除缓冲液的渗透压贡献
    net_protein_Osmolality = protein_Osmolality - protein_buffer_Osmolality

    # 总渗透压
    total_Osmolality = buffer_Osmolality_selected + total_excipient_Osmolality + net_protein_Osmolality
    return total_Osmolality

# Streamlit 应用
def main():
    # 页面标题和描述
    st.title("渗透压计算器")
    st.markdown("""
    **简介**: 本工具用于辅料筛选研究计算生物制剂处方中缓冲液、辅料和蛋白的总渗透压（单位：mOsmol/kg）。
    """)

    # 生物制剂处方渗透压介绍
    st.markdown("""
    ### 生物制剂处方渗透压的重要性
    渗透压是生物制剂处方设计中的一个关键参数，直接影响药物的稳定性和生物活性。以下是一些关键点：
    - **渗透压与细胞活性**：渗透压过高或过低可能导致细胞破裂或皱缩，影响药物的疗效。
    - **渗透压与稳定性**：合适的渗透压有助于维持药物的物理化学稳定性，防止沉淀或聚集。
    - **渗透压与给药途径**：不同的给药途径（如静脉注射、皮下注射）对渗透压有不同的要求。
    """)

    # 创建数据库
    buffer_df, excipient_df = create_database()

    # 用户界面
    st.sidebar.header("处方组成")

    # 目标渗透压输入
    st.sidebar.subheader("目标渗透压")
    target_Osmolality = st.sidebar.number_input("输入目标渗透压 (mOsmol/kg)", min_value=0, value=0, step=10)

    # 蛋白渗透压输入
    st.sidebar.subheader("蛋白渗透压")
    col1, col2 = st.sidebar.columns(2)  # 将缓冲液选择和蛋白渗透压输入放在一行
    with col1:
        protein_buffer_choice = st.selectbox("蛋白渗透压检测时所在的缓冲液", buffer_df["Buffer"])
    with col2:
        protein_Osmolality = st.number_input("目标浓度蛋白渗透压检测值 (mOsmol/kg)", min_value=0, value=100, step=10)

    # 缓冲液选择
    st.sidebar.subheader("Buffer 组成")
    buffer_choice = st.sidebar.selectbox("选择缓冲液", buffer_df["Buffer"])

    # 辅料选择
    st.sidebar.subheader("辅料")
    excipient_choices = st.sidebar.multiselect("选择辅料", excipient_df["Excipient"])

    # 辅料浓度输入
    st.sidebar.subheader("辅料浓度")
    excipient_concentrations = []
    for excipient in excipient_choices:
        concentration = st.sidebar.number_input(f"{excipient} 浓度 (mg/mL)", min_value=0.0, value=1.0, step=0.1)
        excipient_concentrations.append(concentration)

    # 计算渗透压
    if st.sidebar.button("计算渗透压"):
        total_Osmolality = calculate_Osmolality(buffer_df, excipient_df, buffer_choice, excipient_choices, excipient_concentrations, protein_Osmolality, protein_buffer_choice)
        st.success(f"**总渗透压**: {total_Osmolality:.2f} mOsmol/kg")

        # # 判断是否满足目标渗透压
        # if abs(total_Osmolality - target_Osmolality) <= 10:  # 允许10 mOsmol/kg的误差
        #     st.success("处方满足目标渗透压要求！")
        # else:
        #     st.warning(f"处方未满足目标渗透压要求，当前偏差: {abs(total_Osmolality - target_Osmolality):.2f} mOsmol/kg")

# 运行应用
if __name__ == "__main__":
    main()
