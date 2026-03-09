from typing import Optional, List, Literal, Dict, Type
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
import streamlit as st

"""
БАЗОВЫЙ КЛАСС ОБРАБОТЧИКА ДОКУМЕНТА
"""
class BaseDocumentHandler:

    doc_type_name: str = ''
    doc_type_aliases: List[str] = []  # Для классификатора
    
    @classmethod
    def get_schema(cls) -> Type[BaseModel]:
        """Возвращаем Pydantic схему для документа"""
        raise NotImplementedError
    
    @classmethod
    def get_prompt(cls) -> ChatPromptTemplate:
        """Возвращает промпт для извлечения данных"""
        schema = cls.get_schema()
        parser = PydanticOutputParser(pydantic_object=schema)
        
        return ChatPromptTemplate.from_messages([
            ("system", cls.get_system_prompt()),
            ("user", """Извлеки структурированные данные из текста ниже
            {text}
            Верни ответ в JSON формате:
            {format_instructions}""")
        ]).partial(format_instructions=parser.get_format_instructions())
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Системный промпт для LLM"""
        return f"Ты - юрист, анализирующий {cls.doc_type_name}"
    
    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.json(entities)


"""
ОБРАБОТЧИК УСТАВА
"""
class Charter(BaseModel):
    document_type: Literal['устав'] = 'устав'
    full_name_ru: Optional[str] = Field(None, description="Полное наименование на русском")
    short_name_ru: Optional[str] = Field(None, description="Сокращенное наименование на русском")
    full_name_en: Optional[str] = Field(None, description="Полное наименование на английском")
    short_name_en: Optional[str] = Field(None, description="Сокращенное наименование на английском")
    location: Optional[str] = Field(None, description="Место нахождения организации")
    authorized_capital: Optional[str] = Field(None, description = 'Уставной капитал, в рублях или долях для Обществ с Ограниченной Ответственностью')
    governing_bodies_composition: Optional[str] = Field(None, description="Состав органов управления (это могут быть совет директоров, наблюдательный совет, ревизионная комиссия, исполнительный орган и т.д. Укажи все органы управления)")
    supreme_governing_body: Optional[str] = Field(None, description="Высший орган управления")
    executive_body: Optional[str] = Field(None, description="Исполнительный орган")
    election_method: Optional[str] = Field(None, description="Как избирается исполнительный орган")
    term_of_office: Optional[str] = Field(None, description="Срок полномочий исполнительного органа")
    quorum_info: Optional[str] = Field(None, description="Необходимое для принятия решения число участников собрания, Нет - в случае отсутствия информации")
    votes_required: Optional[str] = Field(None, description="Количество голосов, необходимое для принятия решений")
    decisions_formalization: Optional[str] = Field(None, description="Порядок оформления решений/протоколов и выписок")
    power_of_attorney_procedure: Optional[str] = Field(None, description="Порядок выдачи доверенностей ИСКЛЮЧИТЕЛЬНО исполнительного органа")
    eio_authority_scope: Optional[str] = Field(None, description="ПОЛНЫЙ объем полномочий исполнительного органа")
    bond_emission_restrictions: Optional[str] = Field(None, description="Есть ли информация об ограничении объёма или стоимости облигаций или ценных бумаг?")
    bond_emission_ban: Optional[str] = Field(None, description="Есть ли информация о запрете облигаций или ценных бумаг?")
    bond_issuance_decision_body: Optional[str] = Field(None, description="Орган, принимающий решение о размещении облигаций")
    prospectus_approval_body: Optional[str] = Field(None, description="Орган, утверждающий проспект ценных бумаг")
    eio_election_body: Optional[str] = Field(None, description="Орган, избирающий единоличный исполнительный орган")
    charter_registration_date: Optional[str] = Field(None, description="Дата регистрации Устава")

class CharterHandler(BaseDocumentHandler):
    doc_type_name = 'устав'
    doc_type_aliases = ['устав']

    @classmethod
    def get_schema(cls):
        return Charter

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Полное наименование', value=entities['full_name_ru'], key=f'full_name_ru_charter_{doc_id}',
                     # disabled=True
                     )
        col1, col2 = st.columns(2)
        with col1:
            st.text_area('Краткое наименование', value=entities['short_name_ru'], key=f'short_name_ru_{doc_id}',
                          # disabled=True
                          )
            st.text_area('Полное наименование на английском', value=entities['full_name_en'],
                          key=f'full_name_en_{doc_id}',
                         # disabled=True
                          )
            # st.text_input('Дата регистрации Устава', value=entities['charter_registration_date'],
            #               key=f'charter_registration_date_{doc_id}', disabled=True)
        with col2:
            st.text_area('Краткое наименование на английском', value=entities['short_name_en'],
                          key=f'short_name_en_{doc_id}',
                          # disabled=True
                          )
            # st.text_input('Место нахождения организации', value=entities['location'], key=f'location_{doc_id}',
            #               disabled=True)
            st.text_area('Уставный капитал', value=entities['authorized_capital'], key=f'authorized_capital_{doc_id}',
                          # disabled=True
                          )
        st.divider()
        st.text_area('Место нахождения организации', value=entities['location'],
                     key=f'location_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Cостав органов управления', value=entities['governing_bodies_composition'],
                     key=f'governing_bodies_composition_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Высший орган управления', value=entities['supreme_governing_body'],
                     key=f'supreme_governing_body_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Исполнительный орган', value=entities['executive_body'], key=f'executive_body_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Срок полномочий исполнительного органа', value=entities['term_of_office'],
                     key=f'term_of_office_{doc_id}',
                     # disabled=True
                     )
        st.divider()
        st.text_area('Как избирается единый исполнительный орган', value=entities['election_method'],
                     key=f'election_method{doc_id}',
                     # disabled=True
                     )
        st.text_area('Объем полномочий исполнительного органа', value=entities['eio_authority_scope'],
                     key=f'eio_authority_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Количество голосов, необходимое для принятия решений', value=entities['votes_required'],
                     key=f'votes_required_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Порядок выдачи доверенностей исполнительного органа',
                     value=entities['power_of_attorney_procedure'], key=f'power_of_attorney_procedure_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Порядок оформления решений, протоколов или выписок', value=entities['decisions_formalization'],
                     key=f'decisions_formalization_{doc_id}',
                     # disabled=True
                     )
        st.divider()
        st.text_area('🔐 Ограничения по объёму привлечённых средств', value=entities['bond_emission_restrictions'],
                     key=f'bond_emission_restrictions_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Полный запрет на выпуск облигаций', value=entities['bond_emission_ban'],
                     key=f'bond_emission_ban_{doc_id}',
                     # disabled=True
                     )


"""
ОБРАБОТЧИК ЗАКОНА
"""
class Zakon(BaseModel):
    document_type: Literal['закон'] = 'закон'
    full_name_ru: Optional[str] = Field(None, description="Полное наименование на русском")
    short_name_ru: Optional[str] = Field(None, description="Сокращенное наименование на русском")
    full_name_en: Optional[str] = Field(None, description="Полное наименование на английском")
    short_name_en: Optional[str] = Field(None, description="Сокращенное наименование на английском")
    location: Optional[str] = Field(None, description="Место нахождения организации + ссылка на раздел устава")
    authorized_capital: Optional[str] = Field(None, description = 'Уставной капитал + ссылка на раздел устава')
    supreme_governing_body: Optional[str] = Field(None, description="Высший орган управления + ссылка на раздел устава")
    executive_body: Optional[str] = Field(None, description="Исполнительный орган + ссылка на раздел устава")
    election_method: Optional[str] = Field(None, description="Как избирается исполнительный орган + ссылка на раздел устава")
    term_of_office: Optional[str] = Field(None, description="Срок полномочий исполнительного органа + ссылка на раздел устава")
    governing_bodies_composition: Optional[str] = Field(None, description="Состав органов управления + ссылка на раздел устава")
    sheet_count: Optional[str] = Field(None, description="Количество листов в документе")
    charter_registration_date: Optional[str] = Field(None, description="Дата регистрации Устава")
    votes_required: Optional[str] = Field(None, description="Количество голосов, необходимое для принятия решений + ссылка на раздел устава")
    decisions_formalization: Optional[str] = Field(None, description="Порядок оформления решений/протоколов и выписок + ссылка на раздел устава")
    power_of_attorney_procedure: Optional[str] = Field(None, description="Порядок выдачи доверенностей исполнительного органа + ссылка на раздел устава")
    eio_authority_scope: Optional[str] = Field(None, description="Объем полномочий исполнительного органа + ссылка на раздел устава")
    bond_emission_restrictions: Optional[str] = Field(None, description="Есть ли информация об ограничении объёма или стоимости облигаций или ценных бумаг?")
    bond_emission_ban: Optional[str] = Field(None, description="Есть ли информация о запрете облигаций или ценных бумаг?")
    bond_issuance_decision_body: Optional[str] = Field(None, description="Орган, принимающий решение о размещении облигаций + ссылка на раздел устава")
    prospectus_approval_body: Optional[str] = Field(None, description="Орган, утверждающий проспект ценных бума + ссылка на раздел уставаг")
    eio_election_body: Optional[str] = Field(None, description="Орган, избирающий единоличный исполнительный орган + ссылка на раздел устава")
    alternative_decision_confirmation: Optional[str] = Field(None, description="Альтернативный способ подтверждения решений общего собрания, для ООО")

class ZakonHandler(BaseDocumentHandler):
    doc_type_name = 'закон'
    doc_type_aliases = ['закон']

    @classmethod
    def get_schema(cls):
        return Zakon

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Полное наименование', value=entities['full_name_ru'], key=f'full_name_ru_charter_{doc_id}',
                     disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Краткое наименование', value=entities['short_name_ru'], key=f'short_name_ru_{doc_id}',
                          disabled=True)
            st.text_input('Полное наименование на английском', value=entities['full_name_en'],
                          key=f'full_name_en_{doc_id}', disabled=True)
            st.text_input('Дата регистрации Устава', value=entities['charter_registration_date'],
                          key=f'charter_registration_date_{doc_id}', disabled=True)
        with col2:
            st.text_input('Краткое наименование на английском', value=entities['short_name_en'],
                          key=f'short_name_en_{doc_id}', disabled=True)
            st.text_input('Место нахождения организации', value=entities['location'], key=f'location_{doc_id}',
                          disabled=True)
            st.text_input('Уставный капитал', value=entities['authorized_capital'], key=f'authorized_capital_{doc_id}',
                          disabled=True)
        st.divider()
        st.text_area('Cостав органов управления', value=entities['governing_bodies_composition'],
                     key=f'governing_bodies_composition_{doc_id}', disabled=True)
        st.text_area('Высший орган управления', value=entities['supreme_governing_body'],
                     key=f'supreme_governing_body_{doc_id}', disabled=True)
        st.text_area('Исполнительный орган', value=entities['executive_body'], key=f'executive_body_{doc_id}',
                     disabled=True)
        st.text_area('Срок полномочий исполнительного органа', value=entities['term_of_office'],
                     key=f'term_of_office_{doc_id}', disabled=True)
        st.divider()
        st.text_area('Как избирается единый исполнительный орган', value=entities['election_method'],
                     key=f'election_method{doc_id}', disabled=True)
        st.text_area('Объем полномочий исполнительного органа', value=entities['eio_authority_scope'],
                     key=f'eio_authority_{doc_id}', disabled=True)
        st.text_area('Количество голосов, необходимое для принятия решений', value=entities['votes_required'],
                     key=f'votes_required_{doc_id}', disabled=True)
        st.text_area('Порядок выдачи доверенностей исполнительного органа',
                     value=entities['power_of_attorney_procedure'], key=f'power_of_attorney_procedure_{doc_id}',
                     disabled=True)
        st.text_area('Порядок оформления решений, протоколов или выписок', value=entities['decisions_formalization'],
                     key=f'decisions_formalization_{doc_id}', disabled=True)
        st.divider()
        st.text_area('🔐 Ограничения по объёму привлечённых средств', value=entities['bond_emission_restrictions'],
                     key=f'bond_emission_restrictions_{doc_id}', disabled=True)
        st.text_area('Полный запрет на выпуск облигаций', value=entities['bond_emission_ban'],
                     key=f'bond_emission_ban_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК АНКЕТЫ
"""
class Anketa(BaseModel):
    document_type: Literal['анкета'] = 'анкета'
    listing_level: Optional[str] = Field(None, description="Уровень листинга")
    series: Optional[str] = Field(None, description="Серия")
    date: Optional[str] = Field(None, description="Дата заявления")
    full_name_ru: Optional[str] = Field(None, description="Полное наименование на русском")
    short_name_ru: Optional[str] = Field(None, description="Сокращенное наименование на русском")
    full_name_en: Optional[str] = Field(None, description="Полное наименование на английском")
    short_name_en: Optional[str] = Field(None, description="Сокращенное наименование на английском")
    emitent_code: Optional[str] = Field(None, description="Код эмитента")
    registration_date: Optional[str] = Field(None, description="Дата внесения записи в ЕГРЮЛ")
    inn: Optional[str] = Field(None, description="ИНН")
    ogrn: Optional[str] = Field(None, description="ОГРН")
    listing_level: Optional[str] = Field(None, description="Уровень листинга")
    bond_type: Optional[str] = Field(None, description="Тип ценных бумаг")
    bond_form: Optional[str] = Field(None, description="Форма выпуска ценных бумаг")
    bond_form_and_type: Optional[str] = Field(description="Вид и тип облигаций, полное наименование ценных бумаг")
    nominal_value: Optional[str] = Field(None, description="Номинальная стоимость одной ценной бумаги")
    quantity: Optional[str] = Field(None, description="Количество ценных бумаг в выпуске")
    total_issue_volume: Optional[str] = Field(None, description="Общий объем выпуска")
    bond_redemption_date: Optional[str] = Field(None, description="Срок обращения ценной бумаги")
    early_redemption: Optional[str] = Field(None, description="Возможность досрочного погашения")
    default_info: Optional[str] = Field(None, description="Информация о дефолтах ценных бумаг эмитента")
    prospectus_available: Optional[str] = Field(None, description="Наличие Проспекта ценных бумаг?")
    bond_mortgage_coverage: Optional[str] = Field(description = "Облигации с ипотечным покрытием?")
    rating: List[str] = Field(None, description="Значение рейтинга, указывается в таблице Кредитные рейтинги")
    rating_date: List[str] = Field(None, description="Дата присвоения рейтинга")
    rating_agency: List[str] = Field(None, description="Рейтинговое агентство, указывается в таблице Кредитные рейтинги")
    signer_info: Optional[str] = Field(None, description="Полная информация о том, кто подписал документ - ФИО, должность, информации о доверенности и об инных уполномачивающих документах")

class AnketaHandler(BaseDocumentHandler):
    doc_type_name = "анкета"
    doc_type_aliases = ["анкета"]

    @classmethod
    def get_schema(cls):
        return Anketa

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.divider()
        st.text_area('Наименование компании', value=entities['full_name_ru'], key=f'full_name_ru_anketa_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Наименование компании', value=entities['full_name_en'], key=f'full_name_en_anketa_{doc_id}',
                     # disabled=True
                     )
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Уровень листинга', value=entities['listing_level'], key=f'listing_level_{doc_id}',
                          # disabled=True
                          )
            st.text_input('ИНН', value=entities['inn'], key=f'inn_{doc_id}',
                          # disabled=True
                          )
            st.text_input('Код эмитента', value=entities['emitent_code'], key=f'emitent_code_{doc_id}',
                          # disabled=True
                          )
        with col2:
            st.text_input('Серия', value=entities['series'], key=f'series_{doc_id}',
                          # disabled=True
                          )
            st.text_input('ОГРН', value=entities['ogrn'], key=f'ogrn_{doc_id}',
                          # disabled=True
                          )
            st.text_input('Дата регистрации в ЕГРЮЛ', value=entities['registration_date'],
                          key=f'registration_date_{doc_id}',
                          # disabled=True
                          )
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Тип ценных бумаг', value=entities['bond_type'], key=f'bond_type_{doc_id}',
                          # disabled=True
                          )
        with col2:
            st.text_input('Форма выпуска', value=entities['bond_form'], key=f'bond_form_{doc_id}',
                          # disabled=True
                          )
        st.text_area('Вид и тип', value=entities['bond_form_and_type'], key=f'bond_form_and_type_{doc_id}',
                     # disabled=True
                     )
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Количество ценных бумаг', value=entities['quantity'], key=f'quantity_{doc_id}',
                          # disabled=True
                          )
        with col2:
            st.text_input('Номинальная стоимость', value=entities['nominal_value'], key=f'nominal_value_{doc_id}',
                          # disabled=True
                          )
        st.text_area('Общий объём выпуска', value=entities['total_issue_volume'], key=f'total_issue_volume_{doc_id}',
                     # disabled=True
                     )
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Дата погашения ценной бумаги', value=entities['bond_redemption_date'],
                          key=f'bond_redemption_date_{doc_id}',
                          # disabled=True
                          )
            st.text_input('Наличие проспекта ценных бумаг', value=entities['prospectus_available'],
                          key=f'prospectus_available_{doc_id}',
                          # disabled=True
                          )
        with col2:
            st.text_input('Возможность досрочного погашения', value=entities['early_redemption'],
                          key=f'early_redemption_{doc_id}',
                          # disabled=True
                          )
            st.text_input('Облигации с ипотечным покрытием', value=entities['bond_mortgage_coverage'],
                          key=f'bond_mortgage_coverage_{doc_id}',
                          # disabled=True
                          )
        st.divider()
        st.text_area('💀 Информация о дефолтах ценных бумаг', value=entities['default_info'],
                     key=f'default_info_{doc_id}',
                     # disabled=True
                     )
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('🧮 Рейтинг ценных бумаг', value=entities['rating'], key=f'rating_{doc_id}',
                          # disabled=True
                          )
        with col2:
            st.text_input('Рейтинговое агентство', value=entities['rating_agency'], key=f'rating_agency_{doc_id}',
                          # disabled=True
                          )
        st.divider()
        st.text_area('💂‍ Подписант анкеты', value=entities['signer_info'], key=f'signer_info_{doc_id}',
                     # disabled=True
                     )


"""
ОБРАБОТЧИК ЗАЯВЛЕНИЯ
"""
class Application(BaseModel):
    document_type: Literal['заявление'] = 'заявление'
    application_date: Optional[str] = Field(description = 'Дата составления заявления')
    listing_level: Optional[str] = Field(None, description="Уровень листинга")
    provided_service: Optional[str] = Field(description = 'Оказываемая услуга')
    company_name: Optional[str] = Field(None, description = 'Наименование компании')
    bond_name: Optional[str] = Field(None, description="Наименование ценной бумаги")
    series: Optional[str] = Field(None, description="Серия")
    attached_documents: Optional[str] = Field(None, description='Приложенные документы к заявлению, в формате строки, разделённые знаком переноса строки')
    signer_name: Optional[str] = Field(None, description="ФИО подписанта")
    signer_post: Optional[str] = Field(None, description="Должность подписанта")

class ApplicationHandler(BaseDocumentHandler):
    doc_type_name = "заявление"
    doc_type_aliases = ["заявление"]

    @classmethod
    def get_schema(cls):
        return Application

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Название компании', value=entities['company_name'], key=f'company_name_{doc_id}',
                     # disabled=True
                     )
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Дата составления заявления', value=entities['application_date'],
                          key=f'application_date_{doc_id}',
                          # disabled=True
                          )
            st.text_input('Наименование ценной бумаги', value=entities['bond_name'], key=f'bond_name_{doc_id}',
                          # disabled=True
                          )
        with col2:
            st.text_input('Уровень листинга', value=entities['listing_level'], key=f'listing_level_{doc_id}',
                          # disabled=True
                          )
            st.text_input('Серия', value=entities['series'], key=f'series_{doc_id}',
                          # disabled=True
                          )
        st.text_area('Оказываемая услуга', value=entities['provided_service'], key=f'provided_service_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Приложенные документы', value=entities['attached_documents'], key=f'attached_documents_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Должность подписанта', value=entities['signer_post'], key=f'signer_post_{doc_id}',
                     # disabled=True
                     )
        st.text_area('ФИО подписанта', value=entities['signer_name'], key=f'signer_name_{doc_id}',
                     # disabled=True
                     )


"""
ОБРАБОТЧИК ДОГОВОРА ПЕРЕДАЧИ ПОЛНОМОЧИЙ
"""
class AuthorityTransferContract(BaseModel):
    document_type: Literal['договор передачи полномочий'] = 'договор передачи полномочий'
    contract_date: Optional[str] = Field(description = 'Дата подписания договора, в формате строки')
    effective_date: Optional[str] = Field(description = 'Дата вступления в силу, в формате строки')
    parties: Optional[str] = Field(description = 'Стороны договора, в формате строки')
    subject: Optional[str] = Field(description = 'Предмет договора (какие полномочия передаются), в формате строки')
    scope: Optional[str] = Field(description = 'Объём передаваемых полномочий, в формате строки')
    term: Optional[str] = Field(description = 'Срок действия, в формате строки')

class AuthorityTransferContractHandler(BaseDocumentHandler):
    doc_type_name = "договор передачи полномочий"
    doc_type_aliases = ["договор передачи полномочий"]

    @classmethod
    def get_schema(cls):
        return AuthorityTransferContract

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Стороны договора', value=entities['parties'], key=f'parties_{doc_id}',
                     # disabled=True
                     )
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Дата подписания договора', value=entities['contract_date'], key=f'contract_date_{doc_id}',
                          # disabled=True
                          )
        with col2:
            st.text_input('Дата вступления договора в силу', value=entities['effective_date'], key=f'effective_date_{doc_id}',
                          # disabled=True
                          )
        st.text_area('Предмет договора', value=entities['subject'], key=f'subject_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Объём передаваемых полномочий', value=entities['scope'], key=f'scope_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Срок действия договора', value=entities['term'], key=f'term_{doc_id}',
                     # disabled=True
                     )


"""
ОБРАБОТЧИК ДОВЕРЕННОСТИ
"""
class PowerOfAttorney(BaseModel):
    document_type: Literal['доверенность'] = 'доверенность'
    date: Optional[str] = Field(description = 'Дата составления доверенности')
    poa_number: Optional[str] = Field(description = 'Номер доверенности')
    grantor: Optional[str] = Field(description = 'Кто выдаёт доверенность')
    based_on: Optional[str] = Field(None, description = 'Родительская доверенность (при наличии)')
    listing_scope: Optional[str] = Field(description = 'Полномочия, связанные с листингом ценных бумаг, строкой')
    attorneys: Optional[str] = Field(description = 'Представители по доверенности, строкой')
    term: Optional[str] = Field(description = 'Срок действия доверенности')
    signer_name: Optional[str] = Field(description = 'ФИО подписанта')

class PowerAttorneyHandler(BaseDocumentHandler):
    doc_type_name = "доверенность"
    doc_type_aliases = ["доверенность"]

    @classmethod
    def get_schema(cls):
        return PowerOfAttorney

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Представители по доверенности', value=entities['attorneys'], key=f'attorneys_{doc_id}',
                     # disabled=True
                     )
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Дата составления доверенности', value=entities['date'], key=f'date_{doc_id}',
                          # disabled=True
                          )
            st.text_input('Срок действия доверенности', value=entities['term'], key=f'term_{doc_id}',
                          # disabled=True
                          )
        with col2:
            st.text_input('Номер доверенности', value=entities['poa_number'], key=f'poa_number_{doc_id}',
                          # disabled=True
                          )
            st.text_input('ФИО подписанта', value=entities['signer_name'], key=f'signer_name_{doc_id}',
                          # disabled=True
                          )
        st.text_area('Кто выдаёт доверенность', value=entities['grantor'], key=f'grantor_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Объём передаваемых полномочий', value=entities['listing_scope'], key=f'listing_scope_{doc_id}',
                     # disabled=True
                     )


"""
ОБРАБОТЧИК ПРОТОКОЛА
"""
class VotingResult(BaseModel):
    option: Optional[str] = Field(description = 'Вариант голосования')
    votes: Optional[int] = Field(description = 'Количество голосов')

class MeetingProtocol(BaseModel):
    document_type: Literal['протокол'] = 'протокол'
    protocol_number: Optional[str] = Field(description = 'Номер протокола')
    meeting_date: Optional[str] = Field(description = 'Дата проведения собрания')
    agenda: List[str] = Field(description = 'Повестка дня (список вопросов)')
    decisions: List[str] = Field(description = 'Принятые решения')
    voting_results: List[VotingResult] = Field(description = 'Итоги голосования')

class ProtocolHandler(BaseDocumentHandler):
    doc_type_name = "протокол"
    doc_type_aliases = ["протокол"]

    @classmethod
    def get_schema(cls):
        return MeetingProtocol

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Номер протокола', value=entities['protocol_number'],
                          # disabled=True
                          )
        with col2:
            st.text_input('Дата проведения собрания', value=entities['meeting_date'],
                          # disabled=True
                          )
        st.text_area('Повестка дня', value=entities['agenda'], key=f'agenda_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Принятые решения', value=entities['decisions'], key=f'decisions_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Итоги голосования', value=entities['voting_results'], key=f'voting_results_{doc_id}',
                     # disabled=True
                     )

"""
ОБРАБОТЧИК БУХГАЛТЕРСКОЙ ОТЧЕТНОСТИ
"""
class AnnualFinancialReport(BaseModel):
    document_type: Literal['отчетность'] = 'отчетность'
    financial_report_date: Optional[str] = Field(description = 'Дата бухгалтерской отчетности')
    balance_sheet: Optional[str] = Field(description = 'Бухгалтерский баланс')
    financial_results: Optional[str] = Field(description = 'Отчет о финансовых результатах')
    cash_flow: Optional[str] = Field(description = 'Отчет о движении денежных средств')
    explanations: Optional[str] = Field(description = 'Пояснения к бухгалтерскому балансу и отчету о финансовых результатах')
    audit_report_date: Optional[str] = Field(description = 'Дата аудиторского заключения')
    opinion_basis: Optional[str] = Field(description = 'Основание для выражения мнения')
    signature_date: Optional[str] = Field(description = 'Дата подписи')
    audit_employee: Optional[str] = Field(description = 'Сотрудник, который совершил аудит')
    head_of_audit: Optional[str] = Field(description = 'Руководитель аудита')
    ornz_number: Optional[str] = Field(description = 'ОРНЗ руководителя аудита')

class FinancialReportHandler(BaseDocumentHandler):
    doc_type_name = "отчетность"
    doc_type_aliases = ["отчетность"]

    @classmethod
    def get_schema(cls):
        return AnnualFinancialReport

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Дата отчетности', value=entities['financial_report_date'], key=f'financial_report_date_{doc_id}',
                          # disabled=True
                          )
        with col2:
            st.text_input('Дата заключения', value=entities['audit_report_date'], key=f'audit_report_date_{doc_id}',
                          # disabled=True
                          )
        st.text_area('Бухгалтерский баланс', value=entities['balance_sheet'], key=f'balance_sheet_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Отчет о финансовых результатах', value=entities['financial_results'], key=f'financial_results_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Отчет о движении средства', value=entities['cash_flow'], key=f'cash_flow_{doc_id}',
                     # disabled=True
                     )
        st.text_area('Пояснения к бухгалтерскому балансу', value=entities['explanations'], key=f'explanations_{doc_id}',
                     # disabled=True
                     )
        st.divider()
        st.text_area('Основание для выражения мнения', value=entities['opinion_basis'], key=f'opinion_basis_{doc_id}',
                     height = 200,
                     # disabled=True
                     )
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('✒️ Сотрудник, который совершил аудит', value=entities['audit_employee'],
                          key=f'audit_employee_{doc_id}',
                          # disabled=True
                          )
            st.text_input('🤴 Руководитель аудита', value=entities['head_of_audit'],
                          key=f'head_of_audit_{doc_id}',
                          # disabled=True
                          )
        with col2:
            st.text_input('Дата подписи', value=entities['signature_date'], key=f'signature_date_{doc_id}',
                          # disabled=True
                          )
            st.text_input('ОРНЗ Руководителя аудита', value=entities['ornz_number'], key=f'ornz_number_{doc_id}',
                          # disabled=True
                          )

"""
ОБРАБОТЧИК РЕШЕНИЯ УЧАСТНИКА
"""
class AppointmentDecision(BaseModel):
    document_type: Literal['решение участника'] = 'решение участника'
    decision_date: Optional[str] = Field(description = 'Дата решения')
    decision_maker: Optional[str] = Field(description = 'Кто принял решение (орган / лицо')
    decision_summary: Optional[str] = Field(description = 'Суть решения')
    appointed_person: Optional[str] = Field(description = 'Кто избран (ФИО / должность)')
    term: Optional[str] = Field(description = 'Срок полномочий')

class AppointmentDecisionHandler(BaseDocumentHandler):
    doc_type_name = "решение участника"
    doc_type_aliases = ["решение участника"]

    @classmethod
    def get_schema(cls):
        return AppointmentDecision

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Дата решения', value=entities['decision_date'], key=f'decision_date_{doc_id}', disabled=True)
        with col2:
            st.text_input('Срок полномочий', value=entities['term'], key=f'term_{doc_id}', disabled=True)
        st.text_area('Кто принял решение', value=entities['decision_maker'], key=f'decision_maker_{doc_id}', disabled=True)
        st.text_area('Суть решения', value=entities['decision_summary'], key=f'decision_summary_{doc_id}', disabled=True)
        st.text_area('Кто избран', value=entities['appointed_person'], key=f'appointed_person_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК СОГЛАСИЯ НА ОБРАБОТКУ ПЕРСОНАЛЬНЫХ ДАННЫХ
"""
class ConsentToPD(BaseModel):
    document_type: Literal['согласие'] = 'согласие'
    full_name: Optional[str] = Field(description = 'Субъект персональных данных')

class ConsentPDHandler(BaseDocumentHandler):
    doc_type_name = "согласие"
    doc_type_aliases = ["согласие"]

    @classmethod
    def get_schema(cls):
        return ConsentToPD

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Субъект персональных данных', value=entities['full_name'], key=f'full_name_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК ДОГОВОРА ЛИСТИНГА
"""
class ListingContract(BaseModel):
    document_type: Literal['договор листинга'] = 'договор листинга'
    contract_number: Optional[str] = Field(description = 'Регистрационный номер договор')
    contract_date: Optional[str] = Field(description = 'Дата подписания договора')
    company_name: Optional[str] = Field(description = 'Наименование компании эмитента')
    has_amendments: Optional[str] = Field(description = 'Наличие дополнительных соглашений')
    signatory_name: Optional[str] = Field(description = 'ФИО подписанта')
    signatory_title: Optional[str] = Field(description = 'Должность подписанта')

class ListingContractHandler(BaseDocumentHandler):
    doc_type_name = "договор листинга"
    doc_type_aliases = ["договор листинга"]

    @classmethod
    def get_schema(cls):
        return ListingContract

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Название компании', value=entities['company_name'], key=f'company_name_{doc_id}', disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Номер договора', value=entities['contract_number'], key=f'contract_number_{doc_id}', disabled=True)
        with col2:
            st.text_input('Дата подписания', value=entities['contract_date'], key=f'contract_date_{doc_id}', disabled=True)
        st.text_area('Дополнительные соглашения', value=entities['has_amendments'], key=f'has_amendments_{doc_id}', disabled=True)
        st.text_area('Должность подписанта', value=entities['signatory_title'], key=f'signatory_title_{doc_id}', disabled=True)
        st.text_area('ФИО подписанта', value=entities['signatory_name'], key=f'signatory_name_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК ПРОГРАММЫ ОБЛИГАЦИЙ
"""
class BondProgram(BaseModel):
    document_type: Literal['программа'] = 'программа'
    registrar_name: Optional[str] = Field(description = 'Наименование регистрирующей организации')
    full_name: Optional[str] = Field(description = 'Полное фирменное наименование эмитента')
    bond_type: Optional[str] = Field(description = 'Вид облигаций')
    series: Optional[str] = Field(description='Серия биржевых облигаций, ОБЯЗАТЕЛЬНО указывается в начале документа')
    program_duration: Optional[str] = Field(description='Срок действия программы')
    approving_authority: Optional[str] = Field(description='Орган управления, утвердивший программу')
    protocol_details: Optional[str] = Field(description='Дата и номер протокола решения')
    company_address: Optional[str] = Field(description='Юридический адрес эмитента')
    signatory_name: Optional[str] = Field(description='ФИО подписанта')
    signatory_title: Optional[str] = Field(description='Должность подписанта')
    basis_document: Optional[str] = Field(description='Документ, служащий основанием')
    max_nominal_amount: Optional[str] = Field(description='Максимальная сумма номинальных стоимостей облигаций')
    max_maturity_period: Optional[str] = Field(description='Максимальный срок погашения облигаций')
    redemption_form: Optional[str] = Field(description='Форма погашения')
    bond_yield: Optional[str] = Field(description='Доход по облигациям')
    interest_rate_terms: Optional[str] = Field(description='Порядок определения процентной ставки')
    early_redemption_option: Optional[str] = Field(description='Возможность досрочного погашения по усмотрению эмитента? Да или Нет')
    early_redemption_cost: Optional[str] = Field(description='Стоимость досрочного погашения по усмотрению эмитента')
    holder_demand_redemption: Optional[str] = Field(description='Приобретению по требованию владельцев? Да или Нет')
    agreement_based_redemption: Optional[str] = Field(description='Приобретение по соглашению? Да или Нет')
    disclosure_periods: Optional[str] = Field(description='Сроки раскрытия информации')
    disclosure_sources: Optional[str] = Field(description='Источники раскрытия информации')

class BondProgramHandler(BaseDocumentHandler):
    doc_type_name = "программа"
    doc_type_aliases = ["программа"]

    @classmethod
    def get_schema(cls):
        return BondProgram

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Название компании', value=entities['full_name'], key=f'full_name_{doc_id}', disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Регистрирующая организация', value=entities['registrar_name'], key=f'registrar_name_{doc_id}', disabled=True)
            st.text_input('Серия облигаций', value=entities['series'], key=f'series_{doc_id}', disabled=True)
            st.text_input('Утвердивший орган', value=entities['approving_authority'], key=f'approving_authority_{doc_id}', disabled=True)
        with col2:
            st.text_input('Вид облигаций', value=entities['bond_type'], key=f'bond_type_{doc_id}', disabled=True)
            st.text_input('Срок действия программы', value=entities['program_duration'], key=f'program_duration_{doc_id}', disabled=True)
            st.text_input('Дата и номер протокола', value=entities['protocol_details'], key=f'protocol_details_{doc_id}', disabled=True)
        st.text_area('Юридический адрес эмитента', value=entities['company_address'], key=f'company_address_{doc_id}', disabled=True)
        st.text_area('Должность подписанта', value=entities['signatory_title'], key=f'signatory_title_{doc_id}', disabled=True)
        st.text_area('ФИО подписанта', value=entities['signatory_name'], key=f'signatory_name_{doc_id}', disabled=True)
        with col1:
            st.text_input('Максимальная сумма', value=entities['max_nominal_amount'], key=f'max_nominal_amount_{doc_id}', disabled=True)
            st.text_input('Форма погашения', value=entities['redemption_form'], key=f'redemption_form_{doc_id}', disabled=True)
            st.text_input('Досрочное погашение', value=entities['early_redemption_option'], key=f'early_redemption_option_{doc_id}', disabled=True)
            st.text_input('Приобретение по требованию владельца', value=entities['holder_demand_redemption'], key=f'holder_demand_redemption_{doc_id}', disabled=True)
        with col2:
            st.text_input('Максимальный срок', value=entities['max_maturity_period'], key=f'max_maturity_period_{doc_id}', disabled=True)
            st.text_input('Доход по облигациям', value=entities['bond_yield'], key=f'bond_yield_{doc_id}', disabled=True)
            st.text_input('Стоимость досрочного погашения', value=entities['early_redemption_cost'], key=f'early_redemption_cost_{doc_id}', disabled=True)
            st.text_input('Приобретение по соглашению', value=entities['agreement_based_redemption'], key=f'agreement_based_redemption_{doc_id}', disabled=True)
        st.text_area('Порядок определения процентной ставки', value=entities['interest_rate_terms'], key=f'interest_rate_terms_{doc_id}', disabled=True)
        st.text_area('Источники раскрытия информации', value=entities['disclosure_sources'], key=f'disclosure_sources_{doc_id}', disabled=True)
        st.text_area('Сроки раскрытия информации', value=entities['disclosure_periods'], key=f'disclosure_periods_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК РЕШЕНИЯ О ВЫПУСКЕ ОБЛИГАЦИЙ
"""
class BondEdict(BaseModel):
    document_type: Literal['решение о выпуске'] = 'решение о выпуске'
    company_name: Optional[str] = Field(description='Наименование компании эмитента')
    instrument_type: Optional[str] = Field(description = 'Тип инструмента')
    income_form: Optional[str] = Field(description = 'Полное фирменное наименование эмитента')
    bond_series: Optional[str] = Field(description = 'Серия облигаций')
    nominal_value: Optional[str] = Field(description='Номинальная стоимость одной ценной бумаги, в рублях')
    maturity_date: Optional[str] = Field(description='Дата погашения ценной бумаги')
    bond_id: Optional[str] = Field(description='Идентификационный номер ценной бумаги')
    bond_id_date: Optional[str] = Field(description='Дата присвоения идентификационного номера')
    decision_body: Optional[str] = Field(description='Орган, принявший решение')
    decision_date: Optional[str] = Field(description='Дата принятия решения о выпуске')
    protocol_date: Optional[str] = Field(description='Дата протокола')
    protocol_number: Optional[str] = Field(description='Номер протокола')
    company_address: Optional[str] = Field(description='Юридический адрес эмитента')
    signatory_name: Optional[str] = Field(description='ФИО подписанта')
    signatory_title: Optional[str] = Field(description='Должность подписанта')
    basis_document: Optional[str] = Field(description='Документ, служащий основанием')
    basis_document_date: Optional[str] = Field(description='Дата документа, служащего основанием')
    basis_document_number: Optional[str] = Field(description='Номер документа, служащего основанием')
    registration_type: Optional[str] = Field(description='Вид учета прав')
    bond_class: Optional[str] = Field(description='Класс облигаций')

class BondEdictHandler(BaseDocumentHandler):
    doc_type_name = "решение о выпуске"
    doc_type_aliases = ["решение о выпуске"]

    @classmethod
    def get_schema(cls):
        return BondEdict

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Название компании', value=entities['company_name'], key=f'company_name_{doc_id}', disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Тип инструмента', value=entities['instrument_type'], key=f'instrument_type_{doc_id}', disabled=True)
            st.text_input('Номинальная стоимость', value=entities['nominal_value'], key=f'nominal_value_{doc_id}', disabled=True)
            st.text_input('Идентификационный номер', value=entities['bond_id'], key=f'bond_id_{doc_id}', disabled=True)
            st.text_input('Орган, принявший решение', value=entities['decision_body'], key=f'decision_body_{doc_id}', disabled=True)
            st.text_input('Дата протокола', value=entities['protocol_date'], key=f'protocol_date_{doc_id}', disabled=True)
        with col2:
            st.text_input('Серия облигаций', value=entities['bond_series'], key=f'bond_series_{doc_id}', disabled=True)
            st.text_input('Дата погашения', value=entities['maturity_date'], key=f'maturity_date_{doc_id}', disabled=True)
            st.text_input('Дата присвоения номера', value=entities['bond_id_date'], key=f'bond_id_date_{doc_id}', disabled=True)
            st.text_input('Дата принятия решения', value=entities['decision_date'], key=f'decision_date_{doc_id}', disabled=True)
            st.text_input('Номер протокола', value=entities['protocol_number'], key=f'protocol_number_{doc_id}', disabled=True)
        st.text_area('Вид учёта прав', value=entities['registration_type'], key=f'registration_type_{doc_id}', disabled=True)
        st.text_area('Документ, служащий основанием', value=entities['basis_document'], key=f'basis_document_{doc_id}', disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Дата документа', value=entities['basis_document_date'], key=f'basis_document_date_{doc_id}', disabled=True)
        with col2:
            st.text_input('Номер документа', value=entities['basis_document_number'], key=f'basis_document_number_{doc_id}', disabled=True)
        st.text_area('ФИО подписанта', value=entities['signatory_name'], key=f'signatory_name_{doc_id}', disabled=True)
        st.text_area('Должность подписанта', value=entities['signatory_title'], key=f'signatory_title_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК СПРАВКИ О КОЛИЧЕСТВЕ ОБЛИГАЦИЙ
"""
class BondQuantityCertificate(BaseModel):
    document_type: Literal['справка о количестве облигаций'] = 'справка о количестве облигаций'
    certificate_number: Optional[str] = Field(description='Номер справки')
    certificate_date: Optional[str] = Field(description='Дата составления справки')
    program_reg_number: Optional[str] = Field(description='Регистрационный номер программы')
    program_reg_date: Optional[str] = Field(description='Дата регистрации программы')
    bond_quantity: Optional[str] = Field(description='Общее количество облигаций')
    bond_series: Optional[str] = Field(description='Серия облигаций')
    bond_type: Optional[str] = Field(description='Тип облигаций')
    company_name: Optional[str] = Field(description='Полное наименование эмитента')
    company_address: Optional[str] = Field(description='Юридический адрес эмитента')
    contact_details: Optional[str] = Field(description='Контактные данные')
    signatory_name: Optional[str] = Field(description='ФИО подписанта')
    signatory_title: Optional[str] = Field(description='Должность подписанта')

class BondQuantityHandler(BaseDocumentHandler):
    doc_type_name = "справка"
    doc_type_aliases = ["справка"]

    @classmethod
    def get_schema(cls):
        return BondQuantityCertificate

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Название компании', value=entities['company_name'], key=f'company_name_{doc_id}', disabled=True)
        st.text_area('Юридический адрес', value=entities['company_address'], key=f'company_address_{doc_id}', disabled=True)
        st.text_area('Серия облигаций', value=entities['bond_series'], key=f'bond_series_{doc_id}', disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Номер справки', value=entities['certificate_number'], key=f'certificate_number_{doc_id}', disabled=True)
            st.text_input('Регистрационный номер программы', value=entities['program_reg_number'], key=f'program_reg_number_{doc_id}', disabled=True)
            st.text_input('Тип облигаций', value=entities['bond_type'], key=f'bond_type_{doc_id}', disabled=True)
        with col2:
            st.text_input('Дата составления справки', value=entities['certificate_date'], key=f'certificate_date_{doc_id}', disabled=True)
            st.text_input('Дата регистрации программы', value=entities['program_reg_date'], key=f'program_reg_date_{doc_id}', disabled=True)
            st.text_input('Общее количество облигаций', value=entities['bond_quantity'], key=f'bond_quantity_{doc_id}', disabled=True)
        st.text_area('Контактные данные', value=entities['contact_details'], key=f'contact_details_{doc_id}', disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('💂‍ ФИО подписанта', value=entities['signatory_name'], key=f'signatory_name_{doc_id}', disabled=True)
        with col2:
            st.text_input('Должность подписанта', value=entities['signatory_title'], key=f'signatory_title_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК УВЕДОМЛЕНИЯ О ПВО
"""
class Notification(BaseModel):
    document_type: Literal['уведомление о представителе владельца облигаций'] = 'уведомление о представителе владельца облигаций'
    full_name: Optional[str] = Field(description='Полное название уведомляющей организации')
    ambassador_name: Optional[str] = Field(description='Наименование представителя владельца облигаций')
    ambassador_address: Optional[str] = Field(description='Место нахождения представителя владельца облигаций')
    signatory_name: Optional[str] = Field(description='ФИО подписанта')
    signatory_title: Optional[str] = Field(description='Должность подписанта')

class NotificationHandler(BaseDocumentHandler):
    doc_type_name = "уведомление"
    doc_type_aliases = ["уведомление"]

    @classmethod
    def get_schema(cls):
        return Notification

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Уведомляющая организация', value=entities['full_name'], key=f'full_name_{doc_id}', disabled=True)
        st.text_area('Представитель владельца облигаций', value=entities['ambassador_name'], key=f'ambassador_name_{doc_id}', disabled=True)
        st.text_area('Место нахождения представителя владельца облигаций', value=entities['ambassador_address'], key=f'ambassador_address_{doc_id}', disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('💂‍ ФИО подписанта', value=entities['signatory_name'], key=f'signatory_name_{doc_id}', disabled=True)
        with col2:
            st.text_input('Должность подписанта', value=entities['signatory_title'], key=f'signatory_title_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК ИЗМЕНЕНИЙ В УСТАВ
"""
class CharterChanges(BaseModel):
    document_type: Literal['изменения в устав'] = 'изменения в устав'
    date: Optional[str] = Field(description='Дата внесения изменений')
    full_name: Optional[str] = Field(description='Полное название организации')
    subject: Optional[str] = Field(description='Текст изменений')
    signatory_title: Optional[str] = Field(description='Должность подписанта')
    signatory_name: Optional[str] = Field(description='ФИО подписанта')

class CharterChangesHandler(BaseDocumentHandler):
    doc_type_name = "изменения в устав"
    doc_type_aliases = ["изменения в устав"]

    @classmethod
    def get_schema(cls):
        return CharterChanges

    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Полное название организации', value=entities['full_name'], key=f'full_name_{doc_id}', disabled=True)
        st.text_area('Дата внесения изменений', value=entities['date'], key=f'date_{doc_id}', disabled=True)
        st.text_area('Суть изменений', value=entities['subject'], key=f'subject_{doc_id}', disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('💂‍ ФИО подписанта', value=entities['signatory_name'], key=f'signatory_name_{doc_id}', disabled=True)
        with col2:
            st.text_input('Должность подписанта', value=entities['signatory_title'], key=f'signatory_title_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК ДОВЕРЕННОСТИ
"""
class PowerOfAttorneySchema(BaseModel):
    document_type: Literal['доверенность'] = 'доверенность'
    date: Optional[str] = Field(None, description='Дата доверенности')
    poa_number: Optional[str] = Field(None, description='Номер доверенности')
    grantor: Optional[str] = Field(None, description='Кто выдаёт')
    attorneys: Optional[str] = Field(None, description='Представители')
    listing_scope: Optional[str] = Field(None, description='Полномочия по листингу')
    term: Optional[str] = Field(None, description='Срок действия')
    signer_name: Optional[str] = Field(None, description='ФИО подписанта')


class PowerOfAttorneyHandler(BaseDocumentHandler):
    doc_type_name = "доверенность"
    doc_type_aliases = ["доверенность"]
    
    @classmethod
    def get_schema(cls):
        return PowerOfAttorneySchema
    
    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Представители по доверенности', value=entities['attorneys'], key=f'attorneys_{doc_id}', disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.text_input('Дата составления доверенности', value=entities['date'], key=f'date_{doc_id}', disabled=True)
            st.text_input('Срок действия доверенности', value=entities['term'], key=f'term_{doc_id}', disabled=True)
        with col2:
            st.text_input('Номер доверенности', value=entities['poa_number'], key=f'poa_number_{doc_id}', disabled=True)
            st.text_input('ФИО подписанта', value=entities['signer_name'], key=f'signer_name_{doc_id}', disabled=True)
        st.text_area('Кто выдаёт доверенность', value=entities['grantor'], key=f'grantor_{doc_id}', disabled=True)
        st.text_area('Объём передаваемых полномочий', value=entities['listing_scope'], key=f'listing_scope_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК СОГЛАСИЯ НА ОБРАБОТКУ ПЕРСОНАЛЬНЫХ ДАННЫХ
"""
class ConsentSchema(BaseModel):
    document_type: Literal['согласие'] = 'согласие'
    full_name: Optional[str] = Field(None, description='Субъект персональных данных')

class ConsentHandler(BaseDocumentHandler):
    doc_type_name = "согласие"
    doc_type_aliases = ["согласие"]
    
    @classmethod
    def get_schema(cls):
        return ConsentSchema
    
    @classmethod
    def render_view(cls, entities: Dict, doc_id: int):
        st.text_area('Субъект персональных данных', value=entities['full_name'], key=f'full_name_{doc_id}', disabled=True)


"""
ОБРАБОТЧИК БУХГАЛТЕРСКОЙ ОТЧЕТНОСТИ
"""
class FinancialReportSchema(BaseModel):
    document_type: Literal['отчетность'] = 'отчетность'
    reporting_year: Optional[str] = Field(None, description='Год предоставления отчетности')
    full_audit_text: Optional[str] = Field(None, description='Полный текст аудиторского заключения, без изменений')
    audit_fact: Optional[str] = Field(None, description='Факт проведения аудита - что именно проверялось и кем')
    compliance_conclusion: Optional[str] = Field(None, description='Выводы о соответствии отчетности, мнение аудитора')
    basis_for_opinion: Optional[str] = Field(None, description='Основание для выражения мнения, на чём основаны выводы аудитора')
    authorized_capital: Optional[str] = Field(None, description='Величина уставного капитала на конец отчётного года')
    audit_organization: Optional[str] = Field(None, description='Наименование аудиторской организации')
    conclusion_date: Optional[str] = Field(None, description='Дата подписания аудиторского заключения')
    ornz_number: Optional[str] = Field(None, description='ОРНЗ номер аудиторской организации')
    auditor_statement: Optional[str] = Field(None, description='Что говорит аудитор конкретно о проверке')

class DocumentHandlerRegistry:
    """Центральный реестр всех обработчиков документов"""
    
    _handlers: Dict[str, Type[BaseDocumentHandler]] = {}
    
    @classmethod
    def register(cls, handler: Type[BaseDocumentHandler]):
        """Регистрирует обработчик"""
        for alias in handler.doc_type_aliases:
            cls._handlers[alias.lower()] = handler
        return handler
    
    @classmethod
    def get_handler(cls, doc_type: str) -> Optional[Type[BaseDocumentHandler]]:
        """Получает обработчик по типу документа"""
        return cls._handlers.get(doc_type.lower())
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Возвращает все зарегистрированные типы"""
        return list(cls._handlers.keys())


# Регистрируем все обрабтчики и формируем словарь Тип документа - Класс Handler с атрибутами doc_type_name, doc_type_aliases и методами get_schema, render_view
DocumentHandlerRegistry.register(CharterHandler)
DocumentHandlerRegistry.register(CharterChangesHandler)
DocumentHandlerRegistry.register(AnketaHandler)
DocumentHandlerRegistry.register(ApplicationHandler)
DocumentHandlerRegistry.register(AppointmentDecisionHandler)
DocumentHandlerRegistry.register(AuthorityTransferContractHandler)
DocumentHandlerRegistry.register(BondEdictHandler)
DocumentHandlerRegistry.register(BondProgramHandler)
DocumentHandlerRegistry.register(BondQuantityHandler)
DocumentHandlerRegistry.register(ConsentHandler)
DocumentHandlerRegistry.register(ListingContractHandler)
DocumentHandlerRegistry.register(NotificationHandler)
DocumentHandlerRegistry.register(PowerOfAttorneyHandler)
DocumentHandlerRegistry.register(ProtocolHandler)
DocumentHandlerRegistry.register(FinancialReportHandler)