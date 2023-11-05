class TemplateEn:
    @staticmethod
    def filetype_to_name(filetype):
        filetype = str(filetype)
        filetype_dict = {
            "1": "OST",
            "2": "Short Animation",
            "3": "Animation",
            "4": "Other",
            "11": "Main",
            "12": "Side",
            "13": "Short",
            "14": "Event",
            "15": "Bond",
            "16": "Other"
        }

        return filetype_dict[filetype]

    @staticmethod
    def tracktype_to_name(track_type):
        track_type = str(track_type)
        track_type_dict = {
            "0": "OST",
            "1": "Short Animation",
            "2": "Animation",
            "3": "Other",
        }

        return track_type_dict[track_type]


class TemplateZhCn:
    @staticmethod
    def filetype_to_name(filetype):
        filetype = str(filetype)
        filetype_dict = {
            "1": "OST",
            "2": "短篇动画",
            "3": "动画",
            "4": "其它",
            "11": "主线",
            "12": "支线",
            "13": "短篇",
            "14": "活动",
            "15": "羁绊",
            "16": "其它"
        }

        return filetype_dict[filetype]

    @staticmethod
    def tracktype_to_name(track_type):
        track_type = str(track_type)
        track_type_dict = {
            "0": "OST",
            "1": "短篇动画",
            "2": "动画",
            "3": "其它",
        }

        return track_type_dict[track_type]


ALL_FUNC_EN = {"filetype_to_name": TemplateEn.filetype_to_name,
               "tracktype_to_name": TemplateEn.tracktype_to_name}
ALL_FUNC_ZHCN = {"filetype_to_name": TemplateZhCn.filetype_to_name,
                 "tracktype_to_name": TemplateZhCn.tracktype_to_name}
