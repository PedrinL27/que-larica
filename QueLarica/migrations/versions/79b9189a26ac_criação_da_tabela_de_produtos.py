"""Criação da tabela de produtos

Revision ID: 79b9189a26ac
Revises: 
Create Date: 2024-11-15 18:30:13.703140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79b9189a26ac'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('produtos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.Column('descricao', sa.String(length=255), nullable=False),
    sa.Column('preco', sa.Float(), nullable=False),
    sa.Column('imagem', sa.String(length=255), nullable=True),
    sa.Column('restaurante_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['restaurante_id'], ['restaurantes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('produtos')
    # ### end Alembic commands ###
