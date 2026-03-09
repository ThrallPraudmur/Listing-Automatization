class DocumentProcessingError(Exception):
    """Базовое исключение для обрбаотки документов"""
    pass

class LLMError(DocumentProcessingError):
    """Ошибки, связанные с LLM"""
    pass

class AuthenticationError(LLMError):
    """Ошибка аутентификации"""
    pass

class RateLimitError(LLMError):
    """Превышение лимитов запросов"""
    pass

class TimeOutError(LLMError):
    """Превышение таймаута запроса"""
    pass

class OCRError(DocumentProcessingError):
    """Ошибки OCR"""
    pass

class ParsingError(DocumentProcessingError):
    """Ошибки парсинга данных"""
    pass

class ValidationError(DocumentProcessingError):
    """Ошибки валидации данных"""
    pass

class GateweyTimeoutOutError(DocumentProcessingError):
    """Ошибки сервера"""
    pass