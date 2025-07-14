"""Initial migration

Revision ID: deea166656d4
Revises: 
Create Date: 2025-05-13 12:44:27.485819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'deea166656d4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Tạo tất cả các bảng cần thiết ###
    op.create_table('chats',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chats_id'), 'chats', ['id'], unique=False)
    op.create_index(op.f('ix_chats_title'), 'chats', ['title'], unique=False)

    op.create_table('file_metadata',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('original_filename', sa.String(), nullable=True),
    sa.Column('content_type', sa.String(), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('local_disk_path', sa.String(), nullable=False),
    sa.Column('upload_timestamp', sa.DateTime(), nullable=True),
    sa.Column('processing_method', sa.String(), nullable=False),
    sa.Column('gemini_api_file_id', sa.String(), nullable=True),
    sa.Column('gemini_api_upload_timestamp', sa.DateTime(), nullable=True),
    sa.Column('gemini_api_expiry_timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('local_disk_path')
    )
    op.create_index(op.f('ix_file_metadata_gemini_api_file_id'), 'file_metadata', ['gemini_api_file_id'], unique=False)
    op.create_index(op.f('ix_file_metadata_id'), 'file_metadata', ['id'], unique=False)
    op.create_index(op.f('ix_file_metadata_original_filename'), 'file_metadata', ['original_filename'], unique=False)
    
    op.create_table('messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.CheckConstraint("role IN ('user', 'model', 'assistant')", name='check_role'),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)
    op.create_index(op.f('ix_messages_role'), 'messages', ['role'], unique=False)
    op.create_index(op.f('ix_messages_timestamp'), 'messages', ['timestamp'], unique=False)

    op.create_table('message_file_link',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('file_metadata_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['file_metadata_id'], ['file_metadata.id'], ),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ),
    sa.PrimaryKeyConstraint('message_id', 'file_metadata_id')
    )
    # ### Kết thúc phần tạo bảng ###


def downgrade() -> None:
    # ### Xóa các bảng theo thứ tự ngược lại ###
    op.drop_table('message_file_link')
    op.drop_table('messages')
    op.drop_table('file_metadata')
    op.drop_table('chats')
    # ### Kết thúc phần xóa bảng ###