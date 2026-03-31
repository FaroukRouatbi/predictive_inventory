"""add_sales_records_table

Revision ID: bf67fc0aa07a
Revises: 8fb4274c59aa
Create Date: 2026-03-24 15:29:49.223064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf67fc0aa07a'
down_revision: Union[str, Sequence[str], None] = '8fb4274c59aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types first before using them
    productcategory = sa.Enum(
        'ELECTRONICS', 'CLOTHING', 'FOOD', 'BEAUTY', 'HOME', 'SPORTS', 'OTHER',
        name='productcategory'
    )
    currency = sa.Enum('USD', 'CAD', 'EUR', name='currency')
    productcategory.create(op.get_bind(), checkfirst=True)
    currency.create(op.get_bind(), checkfirst=True)

    op.create_table('sales_records',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=False),
    sa.Column('inventory_id', sa.UUID(), nullable=False),
    sa.Column('quantity_sold', sa.Integer(), nullable=False),
    sa.Column('price_at_sale', sa.Integer(), nullable=False),
    sa.Column('sold_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['inventory_id'], ['inventory_items.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_records_inventory_id'), 'sales_records', ['inventory_id'], unique=False)
    op.create_index(op.f('ix_sales_records_product_id'), 'sales_records', ['product_id'], unique=False)
    op.create_index('ix_sales_records_product_sold_at', 'sales_records', ['product_id', 'sold_at'], unique=False)
    op.add_column('inventory_items', sa.Column('reorder_level', sa.Integer(), nullable=False, server_default='10'))
    op.add_column('inventory_items', sa.Column('location', sa.String(), nullable=True))
    op.drop_index(op.f('ix_inventory_items_product_id'), table_name='inventory_items')
    op.create_index(op.f('ix_inventory_items_product_id'), 'inventory_items', ['product_id'], unique=True)
    op.alter_column('products', 'category',
               existing_type=sa.VARCHAR(),
               type_=sa.Enum('ELECTRONICS', 'CLOTHING', 'FOOD', 'BEAUTY', 'HOME', 'SPORTS', 'OTHER', name='productcategory'),
               existing_nullable=False,
               postgresql_using='category::productcategory')
    op.alter_column('products', 'currency',
               existing_type=sa.VARCHAR(length=3),
               type_=sa.Enum('USD', 'CAD', 'EUR', name='currency'),
               existing_nullable=False,
               postgresql_using='currency::currency')


def downgrade() -> None:
    op.alter_column('products', 'currency',
               existing_type=sa.Enum('USD', 'CAD', 'EUR', name='currency'),
               type_=sa.VARCHAR(length=3),
               existing_nullable=False)
    op.alter_column('products', 'category',
               existing_type=sa.Enum('ELECTRONICS', 'CLOTHING', 'FOOD', 'BEAUTY', 'HOME', 'SPORTS', 'OTHER', name='productcategory'),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    op.drop_index(op.f('ix_inventory_items_product_id'), table_name='inventory_items')
    op.create_index(op.f('ix_inventory_items_product_id'), 'inventory_items', ['product_id'], unique=False)
    op.drop_column('inventory_items', 'location')
    op.drop_column('inventory_items', 'reorder_level')
    op.drop_index('ix_sales_records_product_sold_at', table_name='sales_records')
    op.drop_index(op.f('ix_sales_records_product_id'), table_name='sales_records')
    op.drop_index(op.f('ix_sales_records_inventory_id'), table_name='sales_records')
    op.drop_table('sales_records')

    sa.Enum(name='productcategory').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='currency').drop(op.get_bind(), checkfirst=True)