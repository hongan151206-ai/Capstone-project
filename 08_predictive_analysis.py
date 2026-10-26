"""8. Predictive Analysis - LR / SVM / Decision Tree / KNN + GridSearchCV + confusion matrices -> results.json"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

BASE = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "IBM-DS0321EN-SkillsNetwork/datasets/")
COST_SUCCESS, COST_FAIL = 62.0, 165.0  # $M, giá quảng cáo của SpaceX vs đối thủ (giả định minh hoạ)


def load(name):
    try:
        return pd.read_csv(name)
    except FileNotFoundError:
        return pd.read_csv(BASE + name)


def plot_cm(y, y_pred, title, fname):
    cm = confusion_matrix(y, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, ax=ax, fmt="d", cmap="Blues")
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.set_title(title)
    ax.xaxis.set_ticklabels(["did not land", "landed"]); ax.yaxis.set_ticklabels(["did not land", "landed"])
    fig.tight_layout(); fig.savefig(fname, dpi=150); plt.close(fig)
    return cm


def main():
    data = load("dataset_part_2.csv")
    X_df = load("dataset_part_3.csv")
    feature_names = list(X_df.columns)
    Y = data["Class"].to_numpy()

    X = preprocessing.StandardScaler().fit_transform(X_df)
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=2)

    grids = {
        "Logistic Regression": (LogisticRegression(max_iter=1000),
                                {"C": [0.01, 0.1, 1], "penalty": ["l2"], "solver": ["lbfgs"]}),
        "SVM": (SVC(), {"kernel": ("linear", "rbf", "poly", "sigmoid"),
                        "C": np.logspace(-3, 3, 5), "gamma": np.logspace(-3, 3, 5)}),
        "Decision Tree": (DecisionTreeClassifier(random_state=12345),
                          {"criterion": ["gini", "entropy"], "splitter": ["best", "random"],
                           "max_depth": [2 * n for n in range(1, 10)],
                           "max_features": ["sqrt", "log2"],
                           "min_samples_leaf": [1, 2, 4], "min_samples_split": [2, 5, 10]}),
        "KNN": (KNeighborsClassifier(),
                {"n_neighbors": list(range(1, 11)), "algorithm": ["auto", "ball_tree", "kd_tree", "brute"],
                 "p": [1, 2]}),
    }

    rows, fitted, cms = [], {}, {}
    for name, (est, params) in grids.items():
        gs = GridSearchCV(est, params, cv=10).fit(X_train, Y_train)
        pred = gs.predict(X_test)
        cms[name] = plot_cm(Y_test, pred, name, f"cm_{name.replace(' ', '_')}.png")
        fitted[name] = gs
        rows.append({"Model": name, "CV accuracy": round(gs.best_score_, 4),
                     "Test accuracy": round(gs.score(X_test, Y_test), 4),
                     "Precision": round(precision_score(Y_test, pred, zero_division=0), 4),
                     "Recall": round(recall_score(Y_test, pred, zero_division=0), 4),
                     "F1": round(f1_score(Y_test, pred, zero_division=0), 4),
                     "Best params": {k: (v.item() if hasattr(v, "item") else v) for k, v in gs.best_params_.items()}})

    res = pd.DataFrame(rows).sort_values(["Test accuracy", "CV accuracy"], ascending=False)
    best = res.iloc[0]["Model"]
    print(res.to_string(index=False))
    res.to_csv("model_results.csv", index=False)
    plot_cm(Y_test, fitted[best].predict(X_test), f"{best} (best)", "cm_best.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(data=res, x="Model", y="Test accuracy", color="#1f77b4", ax=ax)
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2, p.get_height()), ha="center", va="bottom")
    ax.set_ylim(0, 1.05); ax.set_title("Test accuracy by model"); plt.setp(ax.get_xticklabels(), fontsize=8)
    fig.tight_layout(); fig.savefig("model_comparison.png", dpi=150); plt.close(fig)

    # Insight 1: hệ số lớn nhất của Logistic Regression (đặc trưng ảnh hưởng nhất)
    lr = fitted["Logistic Regression"].best_estimator_
    coef = pd.Series(lr.coef_[0], index=feature_names)
    top = coef.reindex(coef.abs().sort_values(ascending=False).index).head(6)
    fig, ax = plt.subplots(figsize=(6, 4))
    top.sort_values().plot.barh(color=["#d62728" if v < 0 else "#2ca02c" for v in top.sort_values()], ax=ax)
    ax.set_title("Top features - Logistic Regression coefficients"); fig.tight_layout()
    fig.savefig("feature_importance.png", dpi=150); plt.close(fig)

    # Insight 2: chi phí kỳ vọng mỗi lần phóng từ xác suất hạ cánh dự đoán (giả định minh hoạ)
    p = lr.predict_proba(X)[:, 1]
    exp_cost = float((p * COST_SUCCESS + (1 - p) * COST_FAIL).mean())

    cm = cms[best]
    json.dump({
        "best_model": best, "best_test_accuracy": float(res.iloc[0]["Test accuracy"]),
        "best_params": res.iloc[0]["Best params"], "n_test": int(len(Y_test)), "n_train": int(len(Y_train)),
        "table": res.drop(columns=["Best params"]).to_dict("records"),
        "confusion_best": {"TN": int(cm[0, 0]), "FP": int(cm[0, 1]), "FN": int(cm[1, 0]), "TP": int(cm[1, 1])},
        "top_features": {k: round(float(v), 3) for k, v in top.items()},
        "expected_cost_musd": round(exp_cost, 1), "cost_assumption": [COST_SUCCESS, COST_FAIL],
    }, open("results.json", "w"), indent=2)


if __name__ == "__main__":
    main()
