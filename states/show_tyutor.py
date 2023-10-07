from aiogram.dispatcher.filters.state import StatesGroup, State
######atkif
class Atkif_check(StatesGroup):
    tyutor = State()
    attendance = State()
    opportunity = State()

######tarix
class Tarix_check(StatesGroup):
    tyutor = State()
    attendance = State()
    opportunity = State()

######tabbiy_fanlar
class Tabbiy_fanlar_check(StatesGroup):
    tyutor = State()
    attendance = State()
    opportunity = State()

######fizika
class Fizika_check(StatesGroup):
    tyutor = State()
    attendance = State()
    opportunity = State()

########-matematika
class Matematika_check(StatesGroup):
    tyutor = State()
    attendance = State()
    opportunity = State()
######filologiya
class Filologiya_check(StatesGroup):
    tyutor = State()
    attendance = State()
    opportunity = State()

######jismoniy ma'daniyat
class Jismoniy_madaniyat_check(StatesGroup):
    tyutor = State()
    attendance = State()
    opportunity = State()

######ijtimoiy iqtisodiyot
class Ijtimoiy_iqtisodiyot_check(StatesGroup):
    tyutor = State()
    attendance = State()
    opportunity = State()

######san'atshunoslik
class San_atshunoslik_check(StatesGroup):
    tyutor = State()
    attendance = State()
    opportunity = State()

######pedagogika
class Pedagogika_check(StatesGroup):
    tyutor = State()
    attendance = State()
    opportunity = State()


######super admin add:
class Add_database(StatesGroup):
    faculty = State()
    tyutor = State()
    telegram_id = State()

######super admin delete:
class Delete_database(StatesGroup):
    faculty = State()
    tyutor = State()

######super admin update:
class Update_database(StatesGroup):
    faculty = State()
    tyutor = State()
    telegram_id = State()