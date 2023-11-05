class GenerationCache:
    __cache = {}

    @staticmethod
    def generate_cache_data_id(data_type: str, data):
        pass


    @classmethod
    def add_to_cache(cls, lang: str, cache_id: str, data):
        if lang not in cls.__cache.keys():
            cls.__cache[lang] = {}

        cls.__cache[lang][cache_id] = data
        # print(f"Cache added (lang {lang}, id {cache_id})")

    @classmethod
    def get_from_cache(cls, lang: str, cache_id: str):
        # print(f"Cache get (lang {lang}, id {cache_id})")
        return cls.__cache[lang][cache_id]

    @classmethod
    def check_for_cache(cls, lang: str, cache_id: str):
        if lang in cls.__cache.keys() and cache_id in cls.__cache[lang].keys():
            return True
        return False
