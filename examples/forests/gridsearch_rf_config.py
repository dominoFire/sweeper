[
    {
        'classifier_class': 'sklearn.ensemble.RandomForestClassifier',
        'params_grid_search': {
            'n_estimators': range(1, 5, 1),
            'max_features': range(1, 5, 1),
        },
        'cut_list': np.linspace(0.05, 0.95, 10)
    }
]
