"""create_sacred_events_cache_table

Revision ID: b79d6eca48bc
Revises: 003
Create Date: 2025-12-18 13:33:04.459547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b79d6eca48bc'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if table already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'sacred_events_cache' not in existing_tables:
        # Create sacred_events_cache table
        op.create_table(
            'sacred_events_cache',
            sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
            sa.Column('temple_id', sa.BigInteger(), sa.ForeignKey('temples.id', ondelete='CASCADE'), nullable=True),
            sa.Column('event_code', sa.String(length=10), nullable=False),  # 'NAK', 'EK', 'SK', 'PR', 'PM', 'AM'
            sa.Column('event_name', sa.String(length=50), nullable=False),  # 'Rohini', 'Ekadashi', etc.
            sa.Column('event_date', sa.Date(), nullable=False),
            sa.Column('weekday', sa.String(length=10), nullable=True),  # 'Monday', 'Tuesday', etc.
            sa.Column('extra_info', sa.String(length=100), nullable=True),  # Optional (e.g., star name details)
            sa.Column('valid_from', sa.Date(), nullable=True),
            sa.Column('valid_to', sa.Date(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes for fast lookup
        op.create_index('idx_sacred_events_temple_date', 'sacred_events_cache', ['temple_id', 'event_date'])
        op.create_index('idx_sacred_events_code_date', 'sacred_events_cache', ['event_code', 'event_date'])
        op.create_index('idx_sacred_events_date', 'sacred_events_cache', ['event_date'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_sacred_events_date', table_name='sacred_events_cache')
    op.drop_index('idx_sacred_events_code_date', table_name='sacred_events_cache')
    op.drop_index('idx_sacred_events_temple_date', table_name='sacred_events_cache')
    
    # Drop table
    op.drop_table('sacred_events_cache')
