MD-ELM

Detection of originally mislabelled samples in a dataset, with Optimally Pruned Extreme Learning Machine (OP-ELM).

The MDELM function is the core of MD-ELM method, which returns 'likelihood of being a mislabel' score for each sample.

Additional methods are given for running the whole methodology. They generate multiple models, store them in files, 
process the models and combine results. Here is an example code to use them:

    X,Y = cPickle.load(open("data.pkl","rb"))
    mfiles = build_models(X,Y, X.shape[0]/10, k=4, path="./try")

    # run all experiments
    for data in mfiles:
        for elm in data:
            run_model(elm)

    scores = np.zeros((X.shape[0],))
    for data in mfiles:
        found = analyze_models(data)
        scores[found] += 1
    print scores
    print "done"
    
Model files from path="./try" folder can be processed independently with run_model() function on different machines.