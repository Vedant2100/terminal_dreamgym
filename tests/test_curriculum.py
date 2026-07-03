from terminal_dreamgym.curriculum_generator import generate_curricula_from_diagnoses
from terminal_dreamgym.diagnosis import DIAGNOSES_BY_MODE
from terminal_dreamgym.utils import model_dump


def test_overbroad_patch_diagnosis_creates_minimal_patch_curriculum():
    curricula = generate_curricula_from_diagnoses([model_dump(DIAGNOSES_BY_MODE["overbroad_patch"])])
    ids = {curriculum.id for curriculum in curricula}
    assert "minimal_patch_curriculum" in ids


def test_contract_drift_diagnosis_creates_contract_curriculum():
    curricula = generate_curricula_from_diagnoses([model_dump(DIAGNOSES_BY_MODE["contract_drift"])])
    ids = {curriculum.id for curriculum in curricula}
    assert "contract_drift_curriculum" in ids


def test_each_curriculum_has_at_least_three_worlds():
    curricula = generate_curricula_from_diagnoses(
        [
            model_dump(DIAGNOSES_BY_MODE["overbroad_patch"]),
            model_dump(DIAGNOSES_BY_MODE["contract_drift"]),
            model_dump(DIAGNOSES_BY_MODE["swallowed_error"]),
            model_dump(DIAGNOSES_BY_MODE["edited_before_reading_trace"]),
        ]
    )
    assert curricula
    assert all(len(curriculum.worlds) >= 3 for curriculum in curricula)
