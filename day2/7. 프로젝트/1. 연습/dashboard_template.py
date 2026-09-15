# ============================================================================
# 나만의 머신러닝 결과 대시보드 - 뼈대(skeleton) 템플릿
#
# 이 파일은 직접 채우는 파일이 아닙니다.
#   1. 탐색·실험은 노트북(scratch.ipynb)과 experiments/*.py에서 진행합니다.
#   2. experiments/*.py를 실행하면 AGENTS.md 규칙에 따라 AI가 그 결과를
#      자동으로 이 파일에 반영합니다 (runs 리스트, 혼동행렬/잔차 플롯 등).
#   3. 지금 보이는 값은 레이아웃 확인용 예시 데이터이며, 첫 실제 실험 결과가
#      들어오면 자동으로 지워지고 실제 값으로 바뀝니다.
#
# 확인 방법: 터미널에서 streamlit run dashboard_template.py 를 실행하고
# 왼쪽 사이드바에서 페이지(EDA/전처리 결과 / 모델 학습 결과)를 선택하세요.
# 매 실험마다 열어볼 필요는 없고, 여러 번 실험이 쌓여서 결과를 비교하고
# 싶을 때 열어보면 됩니다. 페이지를 추가/삭제하려면 PAGES 딕셔너리를 수정하세요.
#
# 이 대시보드는 개선사이클(문제정의 → Baseline → 지표확인 → Error Analysis
# → 원인분석 → XAI → 개선가설 → 개선 → 재평가 → 반복)의 결과를 페이지별로
# 정리하기 위한 뼈대입니다. 필요 없는 페이지/섹션은 지워도 되고, 순서를 바꿔도 됩니다.
# ============================================================================

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="ML 대시보드", layout="wide")

# TODO(1): 분류면 "classification", 회귀면 "regression"으로 바꿔주세요.
TASK_TYPE = "classification"


# ============================================================================
# 예시 데이터 생성
# 실제로는 이미 학습된 모델의 결과(데이터, 지표, SHAP 값 등)를 불러와서 채우면 됩니다.
# TODO(1): 아래 예시 데이터를 내 프로젝트의 실제 데이터/결과로 바꿔주세요.
# ============================================================================
@st.cache_data
def load_sample_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 150
    return pd.DataFrame(
        {
            "feature_A": rng.normal(50, 10, n),
            "feature_B": rng.normal(20, 5, n),
            "feature_C": rng.integers(0, 5, n),
            "target": rng.integers(0, 2, n) if TASK_TYPE == "classification" else rng.normal(100, 15, n),
        }
    )


data = load_sample_data()

# 지표별 한 줄 설명입니다. 필요한 것만 남기고 지워도 되고, 새 지표를 추가해도 됩니다.
METRIC_EXPLANATIONS = {
    "accuracy": "전체 예측 중 맞춘 비율이에요. 클래스 비율이 균형잡혀 있을 때 특히 믿을 만해요.",
    "precision": "양성이라고 예측한 것 중 실제로 양성인 비율. False Positive를 줄이고 싶을 때 중요해요.",
    "recall": "실제 양성 중 맞춘 비율. False Negative(놓치는 것)를 줄이고 싶을 때 중요해요.",
    "f1": "Precision과 Recall의 조화평균. 둘 다 챙겨야 할 때 참고해요.",
    "rmse": "예측값과 실제값 차이 크기. 값이 작을수록 좋고, 원래 데이터와 단위가 같아 해석이 쉬워요.",
    "mae": "예측값과 실제값 차이의 절대값 평균. RMSE보다 이상치에 덜 민감해요.",
}

# 아래는 레이아웃을 보여주기 위한 예시 실행(run) 목록입니다.
# TODO(2): 실제 실행 결과로 이 리스트를 바꿔주세요.
runs = [
    {"name": "1차 시도 (Baseline)", "설명": "예시 설명 A", "accuracy": 0.70, "precision": 0.65, "recall": 0.60, "f1": 0.62},
    {"name": "2차 시도", "설명": "예시 설명 B", "accuracy": 0.75, "precision": 0.70, "recall": 0.68, "f1": 0.69},
]
runs_df = pd.DataFrame(runs)
metric_keys = [c for c in runs_df.columns if c not in ("name", "설명")]


# ============================================================================
# 페이지 1: EDA/전처리 결과
# ============================================================================
def page_eda() -> None:
    st.title("🔎 EDA/전처리 결과")
    st.caption("모델을 만들기 전에 데이터의 분포와 관계, 전처리 전후 변화를 살펴보는 페이지입니다.")

    st.subheader("데이터 미리보기")
    st.dataframe(data.head(20), use_container_width=True)
    st.caption(f"현재 데이터 크기: {data.shape[0]}행 × {data.shape[1]}열")

    st.divider()

    st.subheader("변수별 분포")
    # TODO(3): 실제로 살펴보고 싶은 컬럼들로 바꿔주세요.
    numeric_cols = [c for c in data.columns if c != "target"]
    selected_col = st.selectbox("분포를 볼 변수를 선택하세요", numeric_cols)
    fig = px.histogram(data, x=selected_col, color="target" if TASK_TYPE == "classification" else None)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("변수 간 상관관계")
    corr = data.corr(numeric_only=True)
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# 페이지 2: 모델 학습 결과
# ============================================================================
def page_model_results() -> None:
    st.title("📊 모델 학습 결과")
    st.caption("여러 번 시도한 실행(run)을 비교하고, 선택한 실행의 지표와 오답 분포를 확인하는 페이지입니다.")

    st.header("📋 내가 시도한 실행들")
    st.dataframe(runs_df, use_container_width=True, hide_index=True)

    selected_run_name = st.selectbox("자세히 볼 실행을 선택하세요", runs_df["name"])
    selected_run = runs_df[runs_df["name"] == selected_run_name].iloc[0]

    st.divider()

    st.header("핵심 지표")
    st.caption(f"선택한 실행: **{selected_run['name']}** — {selected_run['설명']}")
    cols = st.columns(len(metric_keys))
    for col, key in zip(cols, metric_keys):
        with col:
            st.metric(label=key.upper(), value=f"{selected_run[key]:.3f}")
            if key in METRIC_EXPLANATIONS:
                st.caption(METRIC_EXPLANATIONS[key])

    st.divider()

    st.header("🔍 결과 자세히 보기")
    if TASK_TYPE == "classification":
        st.subheader("혼동행렬 (Confusion Matrix)")
        # TODO(4): 아래 혼동행렬을 내 모델의 실제 결과로 바꿔주세요.
        confusion_matrix = np.array([[50, 10], [15, 25]])
        fig = px.imshow(
            confusion_matrix,
            text_auto=True,
            labels=dict(x="예측", y="실제", color="개수"),
            x=["Negative(0)", "Positive(1)"],
            y=["Negative(0)", "Positive(1)"],
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.subheader("잔차 플롯 (Residual Plot)")
        # TODO(4): 아래 예측값(y_pred)과 실제값(y_true)을 내 모델의 실제 결과로 바꿔주세요.
        rng = np.random.default_rng(0)
        y_true = np.linspace(0, 100, 60) + rng.normal(0, 5, 60)
        y_pred = y_true + rng.normal(0, 8, 60)
        fig = px.scatter(x=y_pred, y=y_true - y_pred, labels={"x": "예측값", "y": "잔차 (실제값 - 예측값)"})
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.header("🚨 어디서 틀리고 있나요? (Error Analysis)")
    # TODO(5): 실제로 오류율을 나누어 볼 구간/변수로 이 표를 바꿔주세요.
    error_breakdown = pd.DataFrame(
        {"구간": ["구간 A", "구간 B", "구간 C"], "샘플 수": [40, 70, 30], "오류율": [0.10, 0.25, 0.40]}
    )
    fig = px.bar(error_breakdown, x="구간", y="오류율", text="오류율", color="오류율", color_continuous_scale="Reds")
    fig.update_traces(texttemplate="%{text:.0%}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.header("🧠 모델은 무엇을 보고 판단했나요? (SHAP)")
    st.caption("변수 중요도와 개별 예측에 대한 설명을 확인하는 영역입니다.")

    st.subheader("전체 변수 중요도")
    # TODO(6): 실제 SHAP 값(mean |SHAP value|) 또는 feature_importances_로 바꿔주세요.
    feature_importance = pd.DataFrame(
        {"변수": ["변수 A", "변수 B", "변수 C", "변수 D"], "중요도": [0.40, 0.30, 0.20, 0.10]}
    ).sort_values("중요도")
    fig = px.bar(feature_importance, x="중요도", y="변수", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("개별 샘플 설명")
    # TODO(7): 실제 SHAP waterfall/force plot으로 바꿔주세요. (예: shap.plots.waterfall)
    sample_idx = st.slider("확인할 샘플 번호", 0, len(data) - 1, 0)
    st.dataframe(data.iloc[[sample_idx]], use_container_width=True)

    contrib = pd.DataFrame(
        {"변수": ["변수 A", "변수 B", "변수 C", "변수 D"], "기여도": [0.25, -0.10, 0.05, -0.02]}
    ).sort_values("기여도")
    fig = px.bar(contrib, x="기여도", y="변수", orientation="h", color="기여도", color_continuous_scale="RdBu")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("양수(파란색)는 예측을 높이는 방향, 음수(빨간색)는 예측을 낮추는 방향으로 기여했다는 뜻이에요.")

    st.divider()

    st.header("⚖️ Before / After 비교")
    col_a, col_b = st.columns(2)
    with col_a:
        run_a_name = st.selectbox("Before", runs_df["name"], index=0, key="run_a")
    with col_b:
        run_b_name = st.selectbox("After", runs_df["name"], index=len(runs_df) - 1, key="run_b")
    run_a = runs_df[runs_df["name"] == run_a_name].iloc[0]
    run_b = runs_df[runs_df["name"] == run_b_name].iloc[0]
    compare_cols = st.columns(len(metric_keys))
    for col, key in zip(compare_cols, metric_keys):
        delta = run_b[key] - run_a[key]
        with col:
            st.metric(label=key.upper(), value=f"{run_b[key]:.3f}", delta=f"{delta:+.3f}")

    st.divider()

    st.header("💡 다음 개선 가설")
    st.text_area(
        "이 결과들을 보고, 다음에 시도해볼 검증 가능한 가설을 적어보세요.",
        placeholder="예: 특정 구간에서 오탐/미탐이 많다. 해당 구간을 더 세밀하게 나누거나 "
        "임계값을 조정하면 지표가 올라갈 것이다.",
        height=100,
    )


# ============================================================================
# 사이드바 내비게이션
# ============================================================================
PAGES = {
    "EDA/전처리 결과": page_eda,
    "모델 학습 결과": page_model_results,
}

st.sidebar.header("📌 페이지 선택")
selected_page = st.sidebar.radio("이동할 페이지", list(PAGES.keys()))

st.sidebar.divider()
st.sidebar.subheader("빠른 가이드")
st.sidebar.markdown(
    """
    - **데이터셋**: (experiments 실행 시 자동으로 채워집니다)
    - **문제 유형**: (experiments 실행 시 자동으로 채워집니다)
    - **평가 지표**: (experiments 실행 시 자동으로 채워집니다)
    """
)

PAGES[selected_page]()
