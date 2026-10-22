"""Conservative structured extraction and state safety."""
from nova.order_details import extract_product
from nova.orders import FakeOrderRepository
from nova.repository import InMemoryStateRepository
from nova.service import WorkflowService
from nova.workflow import Step


def test_extracts_product_from_natural_sentence():
    result = extract_product("El cliente compró unos audífonos")
    assert result.product == "audífonos"
    assert not result.needs_clarification


def test_normalizes_accents_for_known_alias():
    assert extract_product("Compró AUDIFONOS").product == "audífonos"


def test_unknown_product_requires_clarification():
    result = extract_product("Un refrigerador")
    assert result.needs_clarification
    assert result.product is None


def test_multiple_products_require_clarification():
    result = extract_product("audífonos y televisor")
    assert result.needs_clarification


def test_negated_product_requires_clarification():
    result = extract_product("No fueron audífonos")
    assert result.needs_clarification


def test_natural_product_description_confirms_record():
    service = WorkflowService(
        InMemoryStateRepository(), order_repository=FakeOrderRepository()
    )
    service.handle_message("a", "Quiero devolver unos audífonos")
    service.handle_message("a", "Creo que era la 83921")
    response, state = service.handle_message("a", "El cliente compró unos audífonos")
    assert state.order_id == "83921"
    assert state.pending_order_id is None
    assert state.next_step == Step.GET_ORDER
    assert "coinciden" in response


def test_ambiguous_product_keeps_candidate():
    service = WorkflowService(
        InMemoryStateRepository(), order_repository=FakeOrderRepository()
    )
    service.handle_message("a", "Quiero devolver unos audífonos")
    service.handle_message("a", "83921")
    response, state = service.handle_message("a", "audífonos y televisor")
    assert "único producto" in response
    assert state.order_id is None
    assert state.pending_order_id == "83921"
    assert state.next_step == Step.ASK_FOR_ORDER_DETAILS


def test_blank_aliases_never_match_unrelated_text(monkeypatch):
    from nova import order_details

    monkeypatch.setattr(order_details, "PRODUCT_ALIASES", {
        "audífonos": ("", "   "),
        "televisor": ("televisor",),
    })
    result = extract_product("El cliente compró unos audífonos")
    assert result.product is None
    assert result.needs_clarification


def test_blank_aliases_do_not_create_false_second_product(monkeypatch):
    from nova import order_details

    monkeypatch.setattr(order_details, "PRODUCT_ALIASES", {
        "audífonos": ("", "   "),
        "televisor": ("televisor",),
    })
    result = extract_product("El cliente compró un televisor")
    assert result.product == "televisor"
    assert not result.needs_clarification


def test_uncertain_product_requires_clarification():
    result = extract_product("Creo que eran unos audífonos, pero no estoy segura")
    assert result.needs_clarification
    assert result.product is None


def test_uncertainty_does_not_confirm_matching_order():
    service = WorkflowService(
        InMemoryStateRepository(), order_repository=FakeOrderRepository()
    )
    service.handle_message("uncertain", "Quiero devolver unos audífonos")
    service.handle_message("uncertain", "83921")
    response, state = service.handle_message(
        "uncertain", "Creo que eran audífonos, pero no estoy seguro"
    )
    assert "único producto" in response
    assert state.pending_order_id == "83921"
    assert state.order_id is None
    assert state.next_step == Step.ASK_FOR_ORDER_DETAILS


def test_clear_confirmation_after_uncertainty_can_advance():
    service = WorkflowService(
        InMemoryStateRepository(), order_repository=FakeOrderRepository()
    )
    service.handle_message("clarify", "Quiero devolver unos audífonos")
    service.handle_message("clarify", "83921")
    service.handle_message("clarify", "Tal vez eran audífonos")
    _, state = service.handle_message("clarify", "Confirmo que eran audífonos")
    assert state.order_id == "83921"
    assert state.pending_order_id is None
    assert state.next_step == Step.GET_ORDER


class StubExtractor:
    def __init__(self, result):
        self.result = result

    def extract(self, message):
        return self.result


def test_injected_extractor_can_confirm_corroborated_order():
    from nova.order_details import ProductExtraction
    service = WorkflowService(
        InMemoryStateRepository(), order_repository=FakeOrderRepository(),
        product_extractor=StubExtractor(ProductExtraction("audífonos", False)),
    )
    service.handle_message("stub", "Quiero devolver unos audífonos")
    service.handle_message("stub", "83921")
    _, state = service.handle_message("stub", "unos auriculares inalámbricos")
    assert state.order_id == "83921"


def test_injected_uncertain_extraction_never_confirms():
    from nova.order_details import ProductExtraction
    service = WorkflowService(
        InMemoryStateRepository(), order_repository=FakeOrderRepository(),
        product_extractor=StubExtractor(ProductExtraction("audífonos", True)),
    )
    service.handle_message("stub", "Quiero devolver unos audífonos")
    service.handle_message("stub", "83921")
    _, state = service.handle_message("stub", "Creo que eran auriculares")
    assert state.order_id is None
    assert state.pending_order_id == "83921"


def test_injected_unknown_product_cannot_bypass_validation():
    from nova.order_details import ProductExtraction
    service = WorkflowService(
        InMemoryStateRepository(), order_repository=FakeOrderRepository(),
        product_extractor=StubExtractor(ProductExtraction("inventado", False)),
    )
    service.handle_message("stub", "Quiero devolver unos audífonos")
    service.handle_message("stub", "83921")
    _, state = service.handle_message("stub", "un artículo")
    assert state.order_id is None
    assert state.pending_order_id == "83921"
