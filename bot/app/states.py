from aiogram.fsm.state import StatesGroup, State

class SellerShopStates(StatesGroup):
    phone = State()
    name = State()
    city = State()
    location = State()
    landmark = State()


class SellerPartStates(StatesGroup):
    car_model = State()
    part_name = State()


class PartEditStates(StatesGroup):
    waiting_new_name = State()


class SearchStates(StatesGroup):
    city = State()
    query = State()


class FeedbackStates(StatesGroup):
    waiting_text = State()