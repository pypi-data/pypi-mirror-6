import np

class Multichain(object):

    def __init__(self):
        pass
    
    def call_mcmc((model_class, data, dbname, rnd, kwargs)):
        # Randomize seed
        np.random.seed(int(rnd))
        
        model = model_class(data, **kwargs)
        model.mcmc(dbname=dbname)
        model.mcmc_model.db.close()

    def create_tag_names(tag, chains=None):
        import multiprocessing
        if chains is None:
            chains = multiprocessing.cpu_count()
            tag_names = []
        # Create copies of data and the corresponding db names
        for chain in range(chains):
            tag_names.append("db/mcmc%s%i.pickle"% (tag,chain))

        return tag_names

    def load_parallel_chains(model_class, data, tag, kwargs, chains=None,
                             test_convergance=True, combine=True):
        tag_names = create_tag_names(tag, chains=chains)
        models = []
        for tag_name in tag_names:
            model = model_class(data, **kwargs)
            model.mcmc_load_from_db(tag_name)
            models.append(model)

        if test_convergance:
            Rhat = test_chain_convergance(models)
            print Rhat

        if combine:
            m = combine_chains(models, model_class, data, kwargs)
            return m

        return models

    def combine_chains(models, model_class, data, kwargs):
        """Combine multiple model runs into one final model (make sure
        that chains converged)."""
        # Create model that will contain the other traces
        m = copy(models[0])

        # Loop through models and combine chains
        for model in models[1:]:
            m._set_traces(m.group_params, mcmc_model=model.mcmc_model, add=True)
            m._set_traces(m.group_params_tau, mcmc_model=model.mcmc_model, add=True)
            m._set_traces(m.subj_params, mcmc_model=model.mcmc_model, add=True)

        return m

    def run_parallel_chains(model_class, data, tag, load=False, cpus=None,
                            chains=None, **kwargs):
        import multiprocessing
        if cpus is None:
            cpus = multiprocessing.cpu_count()

        tag_names = create_tag_names(tag, chains=chains)
        # Parallel call
        if not load:
            rnds = np.random.rand(len(tag_names))*10000
            pool = multiprocessing.Pool(processes=cpus)
            pool.map(call_mcmc, [(model_class, data, tag_name, rnd,
                                  kwargs) for tag_name,rnd in zip(tag_names, rnds)])

        models = load_parallel_chains(model_class, data, tag_names, kwargs)

        return models
