"""8. Predictive Analysis - LR / SVM / Decision Tree / KNN + GridSearchCV + confusion matrices"""
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
from sklearn.metrics import confusion_matrix

BASE = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "IBM-DS0321EN-SkillsNetwork/datasets/")


def load(name):
    try:
        return pd.read_csv(name)
    except FileNotFoundError:
        return pd.read_csv(BASE + name)


def plot_cm(y, y_pred, title):
    cm = confusion_matrix(y, y_pred)
    ax = plt.subplot()
    sns.heatmap(cm, annot=True, ax=ax, fmt="d")
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.set_title(title)
    ax.xaxis.set_ticklabels(["did not land", "landed"]); ax.yaxis.set_ticklabels(["did not land", "landed"])
    plt.savefig(f"cm_{title.replace(' ', '_')}.png", dpi=150); plt.close()


def main():
    data = load("dataset_part_2.csv")
    X = load("dataset_part_3.csv")
    Y = data["Class"].to_numpy()

    X = preprocessing.StandardScaler().fit_transform(X)
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

    rows = []
    for name, (est, params) in grids.items():
        gs = GridSearchCV(est, params, cv=10).fit(X_train, Y_train)
        test_acc = gs.score(X_test, Y_test)
        rows.append({"Model": name, "CV accuracy": gs.best_score_, "Test accuracy": test_acc,
                     "Best params": gs.best_params_})
        plot_cm(Y_test, gs.predict(X_test), name)

    res = pd.DataFrame(rows).sort_values("Test accuracy", ascending=False)
    print(res.to_string(index=False))
    res.to_csv("model_results.csv", index=False)

    plt.figure(figsize=(6, 4))
    sns.barplot(data=res, x="Model", y="Test accuracy", color="#1f77b4")
    plt.ylim(0, 1); plt.title("Test accuracy by model"); plt.tight_layout()
    plt.savefig("model_comparison.png", dpi=150)


if __name__ == "__main__":
    main()
