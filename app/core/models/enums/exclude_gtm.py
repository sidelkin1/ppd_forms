from enum import Enum


class ExcludeGTM(str, Enum):
    branch = "ЗБС"
    drill = "ВНС"
    recomplete = "ПДГ"
    dual = "ОРЭ"
    frac = "ГРП"
    reactivate = "ВБД"
    stack = "ИДФ"
    commingle = "Приобщение"
    perf = "Дострел"
    acid = "ОПЗ"
    reperf = "Перестрел"
    stimulate = "ИДН"
    squeeze = "РИР"
