class Enum:
    '''
    Namespace and base class for enum generation.
    '''

    @staticmethod
    def generate(enumName, names):
        '''
        Generate simple enum class from list of names, with class fields
        with names being upper case of its values.
        '''
        generated_dict = {name.upper(): name for name in names}
        generated_dict["names"] = list(map(str.upper, names))
        generated_dict["values"] = list(names)
        out = type(enumName, (Enum,), generated_dict)
        # for name in names:
        #     setattr(out, name.upper(), name)
        return out

    @staticmethod
    def generateMapped(enumName, pairs):
        '''
        Generate simple enum class from mapping, with class fields with names
        from pairs.keys() and values from according pairs.values().
        '''
        if isinstance(pairs, dict):
            pairs = pairs.items()
        generated_dict = {k.upper(): v for k, v in pairs}
        generated_dict["names"] = [k.upper() for k, v in pairs]
        generated_dict["values"] = [v for k, v in pairs]
        out = type(enumName, (Enum,), generated_dict)
        return out

