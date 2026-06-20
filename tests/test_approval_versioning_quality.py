from services.approval_workflow_service import (
    approval_gate,
    can_transition,
    hero_approval_workflow,
    transition_item,
)
from services.document_version_service import (
    compare_obligation_sets,
    document_version_record,
    hero_document_version_diff,
)
from services.quality_learning_service import workflow_learning_summary


def test_approval_workflow_blocks_invalid_role_transition():
    items = hero_approval_workflow()
    item = next(row for row in items if row['artifact_id'] == 'REQ-SAF-T-001')
    decision = can_transition(item['state'], 'Approved', 'Product Manager')
    assert decision['allowed'] is False
    updated = transition_item(item, 'Approved', actor='Marco', role='Product Manager', reason='Should be compliance owned')
    assert updated['state'] == item['state']
    assert updated['last_transition']['allowed'] is False


def test_approval_workflow_allows_compliance_approval_after_review():
    item = {'artifact_id':'REL-1','artifact_type':'Release note','title':'Safer copy','state':'Compliance reviewed','owner':'Support','history':[]}
    updated = transition_item(item, 'Approved', actor='Reviewer', role='Compliance Reviewer', reason='Evidence reviewed')
    assert updated['state'] == 'Approved'
    assert updated['last_transition']['allowed'] is True
    gate = approval_gate([updated])
    assert gate['status'] == 'Ready'


def test_document_version_hash_and_obligation_diff():
    rec = document_version_record(document_id='D1', version='v1', text=' SAF-T invoice validation  ', imported_by='Marco')
    assert rec['hash']
    diff = compare_obligation_sets(
        [{'obligation_id':'O1','obligation':'Validate invoice'}],
        [{'obligation_id':'O1','obligation':'Validate invoice before export'}, {'obligation_id':'O2','obligation':'Block missing tax id'}],
    )
    assert diff['changed_count'] == 1
    assert diff['added_count'] == 1


def test_hero_document_version_diff_includes_downstream_impact():
    diff = hero_document_version_diff()
    assert diff['previous_document']['hash'] != diff['current_document']['hash']
    assert diff['diff']['added_count'] >= 1
    assert diff['impacted_downstream']


def test_quality_learning_summary_shape():
    summary = workflow_learning_summary(limit=10)
    assert 'runs_total' in summary
    assert 'workflow_mix' in summary
    assert 'metric_trends' in summary
