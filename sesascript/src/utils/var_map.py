class VarMap(dict[str, str]):
    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        return key
