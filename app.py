import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# タイトル
st.title("OCL断面図")

# パラメータをスライダーで設定（単位：nm、0-1000nm、20nm刻み）
ocl_height = st.slider("OCL高さ (台座の高さ, nm)", min_value=0, max_value=1000, value=700, step=20)
ocl_thickness = st.slider("OCL厚さ (半球の高さ, nm)", min_value=0, max_value=1000, value=400, step=20)
horn_width = st.slider("角の幅 (nm)", min_value=0, max_value=1000, value=240, step=20)
horn_height = st.slider("角の高さ (nm)", min_value=0, max_value=1000, value=250, step=20)
horn_pitch = st.slider("角のピッチ (nm)", min_value=0, max_value=1000, value=320, step=20)

# 図を描く準備
fig, ax = plt.subplots(figsize=(12, 8))

# OCLの幅を固定（1画素 = 1.0μm = 1000nm）
ocl_base_width = 1000  # nm固定

# 台座（矩形部分）の高さ
base_height = ocl_height

# 扁平率を固定（1.05）
flattening = 1.05
a = ocl_base_width / 2  # 横半径 = 500nm（固定）

# OCL曲面上の高さを計算する関数（扁平率固定の楕円）
def ocl_surface_height(x_pos):
    if abs(x_pos) <= a and ocl_thickness > 0:
        normalized_height = np.sqrt(1 - (x_pos/a)**2)
        return base_height + ocl_thickness * normalized_height
    else:
        return base_height

# 3本の角の位置
positions = [-horn_pitch, 0, horn_pitch]

# 角の統一形状を作成（底面をOCL曲面に沿わせる）
def create_horn_with_ocl_base(x_center):
    """
    角の形状を作成
    - 底面はOCL曲面に沿う
    - 上部の形状は統一
    """
    # 底面の範囲
    x_left = x_center - horn_width/2
    x_right = x_center + horn_width/2
    
    # 中心でのOCL高さ
    y_center = ocl_surface_height(x_center)
    
    # 底面：OCL曲面に沿う（細かくサンプリング）
    n_base_points = 50
    x_base = np.linspace(x_left, x_right, n_base_points)
    y_base = np.array([ocl_surface_height(x) for x in x_base])
    
    # 左側の辺：統一形状
    n_side_points = 40
    t_values = np.linspace(0, 1, n_side_points)
    
    x_left_side = []
    y_left_side = []
    
    for t in t_values:
        # X座標：左端から中心へ
        x_current = x_left + (x_center - x_left) * t
        x_left_side.append(x_current)
        
        # Y座標：その位置のOCL曲面 + 統一された高さカーブ
        y_ocl_at_x = ocl_surface_height(x_current)
        height_curve = horn_height * (1 - (1-t)**2)  # 二次関数カーブ
        y_left_side.append(y_ocl_at_x + height_curve)
    
    x_left_side = np.array(x_left_side)
    y_left_side = np.array(y_left_side)
    
    # 右側の辺：統一形状（対称）
    x_right_side = []
    y_right_side = []
    
    for t in t_values:
        # X座標：中心から右端へ
        x_current = x_center + (x_right - x_center) * t
        x_right_side.append(x_current)
        
        # Y座標：その位置のOCL曲面 + 統一された高さカーブ
        y_ocl_at_x = ocl_surface_height(x_current)
        height_curve = horn_height * (1 - t**2)  # 二次関数カーブ
        y_right_side.append(y_ocl_at_x + height_curve)
    
    x_right_side = np.array(x_right_side)
    y_right_side = np.array(y_right_side)
    
    # 輪郭を結合（底面 → 右側 → 左側逆順）
    x_horn = np.concatenate([x_base, x_right_side[::-1][1:], x_left_side[::-1][1:-1]])
    y_horn = np.concatenate([y_base, y_right_side[::-1][1:], y_left_side[::-1][1:-1]])
    
    return x_horn, y_horn

# 各角を描く（OCLの背面、zorder=1）
for x_pos in positions:
    x_horn, y_horn = create_horn_with_ocl_base(x_pos)
    
    # 角全体を塗りつぶす（zorder=1でOCLの背面）
    ax.fill(x_horn, y_horn, color='magenta', edgecolor='darkmagenta', linewidth=1.5, zorder=1)

# OCL台座（矩形部分）と半球を描画

# OCL上面の半球曲線を計算
n_points = 500
x_lens = np.linspace(-a, a, n_points)
y_lens = np.array([ocl_surface_height(x) for x in x_lens])

# OCL全体の輪郭（台座 + 半球）
x_ocl_total = np.concatenate([[-a, -a], x_lens, [a, a]])
y_ocl_total = np.concatenate([[0, base_height], y_lens, [base_height, 0]])

# OCLを塗りつぶす（zorder=2で角の前面、透明度をつける）
ax.fill(x_ocl_total, y_ocl_total, color='gold', edgecolor='black', linewidth=2, label='OCL', zorder=2, alpha=0.85)

# グラフの設定
ax.set_xlabel("X座標 (nm)", fontsize=14)
ax.set_ylabel("高さ (nm)", fontsize=14)
ax.set_title("OCL断面図（1.0μm × 1.0μm画素、扁平率1.05固定）", fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.2, linestyle='--', zorder=0)
ax.set_aspect('equal')

# 表示範囲を調整
margin = 100
total_height = base_height + ocl_thickness + horn_height
ax.set_xlim(-a - margin, a + margin)
ax.set_ylim(-50, total_height + 150)

# 背景色
ax.set_facecolor('#F0F0F8')
fig.patch.set_facecolor('white')

# 凡例
handles = [plt.Rectangle((0,0),1,1, color='gold', label='OCL (1.0μm × 1.0μm)'),
           plt.Rectangle((0,0),1,1, color='magenta', label='角')]
ax.legend(handles=handles, loc='upper right', fontsize=12)

# パラメータ情報を表示
param_text = f"OCL: 1.0μm × 1.0μm (固定), 扁平率: {flattening} (固定)\n"
param_text += f"台座高さ(OCL高さ): {ocl_height}nm, 半球高さ(OCL厚さ): {ocl_thickness}nm\n"
param_text += f"角幅: {horn_width}nm, 角高さ: {horn_height}nm, 角ピッチ: {horn_pitch}nm"
ax.text(0.5, 0.02, param_text, transform=ax.transAxes, 
        fontsize=9, ha='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 図を表示
st.pyplot(fig)
