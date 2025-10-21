"""initial

Revision ID: 86a4a584b12c
Revises: 
Create Date: 2025-10-21T10:02:21.652922Z
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '86a4a584b12c'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('audits',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('client_id', sa.String()),
        sa.Column('contact_id', sa.String(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('audit_types', sa.JSON()),
        sa.Column('overall_score', sa.Integer()),
        sa.Column('lighthouse_perf', sa.Integer()),
        sa.Column('lighthouse_accessibility', sa.Integer()),
        sa.Column('lighthouse_best_practices', sa.Integer()),
        sa.Column('lighthouse_seo', sa.Integer()),
        sa.Column('cwv_json', sa.JSON()),
        sa.Column('tech_stack_json', sa.JSON()),
        sa.Column('summary', sa.Text()),
        sa.Column('report_url', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('status', sa.String(), nullable=False),
    )
    op.create_table('audit_findings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('audit_id', sa.String(), sa.ForeignKey('audits.id', ondelete='CASCADE')),
        sa.Column('category', sa.String()),
        sa.Column('severity', sa.String()),
        sa.Column('code', sa.String()),
        sa.Column('message', sa.Text()),
        sa.Column('target', sa.Text()),
        sa.Column('extra', sa.JSON()),
    )

def downgrade():
    op.drop_table('audit_findings')
    op.drop_table('audits')
