#!/usr/bin/env python3
"""
Admin User Creation Script for BiliNote SaaS

This script creates a new admin user or promotes an existing user to admin.

Usage:
    python -m scripts.create_admin

Environment Variables Required:
    DATABASE_URL - Database connection string
"""

import sys
import os
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db.engine import SessionLocal
from app.db.user_dao import UserDAO
from app.core.security import get_password_hash


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 10:
        return False, "密码至少需要10个字符"

    if not any(char.isupper() for char in password):
        return False, "密码必须包含至少一个大写字母"

    if not any(char.islower() for char in password):
        return False, "密码必须包含至少一个小写字母"

    if not any(char.isdigit() for char in password):
        return False, "密码必须包含至少一个数字"

    # Check for common weak passwords
    common_passwords = [
        'password', '123456789', 'qwerty123', 'abc123456',
        '1234567890', 'password123', 'admin123', 'welcome123'
    ]
    if password.lower() in common_passwords:
        return False, "密码过于简单，请选择更强的密码"

    return True, ""


def create_new_admin():
    """Create a new admin user"""
    print("\n=== 创建新管理员用户 ===\n")

    email = input("邮箱地址: ").strip()
    if not email or '@' not in email:
        print("❌ 邮箱地址无效")
        return False

    full_name = input("姓名 (可选): ").strip()
    if not full_name:
        full_name = "Admin User"

    # Password input with validation
    while True:
        password = getpass("密码 (至少10字符，需包含大小写字母和数字): ")
        is_valid, error_msg = validate_password(password)

        if not is_valid:
            print(f"❌ {error_msg}")
            continue

        password_confirm = getpass("确认密码: ")
        if password != password_confirm:
            print("❌ 两次输入的密码不一致")
            continue

        break

    # Create user in database
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = UserDAO.get_user_by_email(db, email)
        if existing_user:
            print(f"❌ 用户 {email} 已存在")
            promote = input("是否将其提升为管理员? (y/n): ").strip().lower()
            if promote == 'y':
                existing_user.is_superuser = True
                db.commit()
                print(f"✅ 用户 {email} 已提升为管理员")
                return True
            return False

        # Create new user
        hashed_password = get_password_hash(password)
        user = UserDAO.create_user(
            db=db,
            email=email,
            password=hashed_password,
            full_name=full_name
        )

        # Set as superuser
        user.is_superuser = True
        db.commit()
        db.refresh(user)

        print(f"\n✅ 管理员用户创建成功!")
        print(f"   ID: {user.id}")
        print(f"   邮箱: {user.email}")
        print(f"   姓名: {user.full_name}")
        print(f"   管理员权限: {user.is_superuser}")

        return True

    except Exception as e:
        db.rollback()
        print(f"\n❌ 创建失败: {e}")
        return False
    finally:
        db.close()


def promote_existing_user():
    """Promote an existing user to admin"""
    print("\n=== 提升现有用户为管理员 ===\n")

    email = input("要提升的用户邮箱: ").strip()
    if not email:
        print("❌ 邮箱地址不能为空")
        return False

    db = SessionLocal()
    try:
        user = UserDAO.get_user_by_email(db, email)

        if not user:
            print(f"❌ 用户 {email} 不存在")
            return False

        if user.is_superuser:
            print(f"ℹ️  用户 {email} 已经是管理员")
            return True

        # Confirm promotion
        print(f"\n用户信息:")
        print(f"   ID: {user.id}")
        print(f"   邮箱: {user.email}")
        print(f"   姓名: {user.full_name}")
        print(f"   注册时间: {user.created_at}")

        confirm = input("\n确认提升此用户为管理员? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            return False

        # Promote to admin
        user.is_superuser = True
        db.commit()

        print(f"\n✅ 用户 {email} 已提升为管理员")
        return True

    except Exception as e:
        db.rollback()
        print(f"\n❌ 提升失败: {e}")
        return False
    finally:
        db.close()


def list_admins():
    """List all admin users"""
    print("\n=== 当前管理员列表 ===\n")

    db = SessionLocal()
    try:
        # Get all users
        from app.models.user_model import User
        admins = db.query(User).filter(User.is_superuser == True).all()

        if not admins:
            print("目前没有管理员用户")
            return

        print(f"共 {len(admins)} 位管理员:\n")
        for admin in admins:
            print(f"  • {admin.email}")
            print(f"    姓名: {admin.full_name}")
            print(f"    ID: {admin.id}")
            print(f"    注册时间: {admin.created_at}")
            print()

    except Exception as e:
        print(f"\n❌ 查询失败: {e}")
    finally:
        db.close()


def main():
    """Main function"""
    print("\n" + "="*60)
    print("BiliNote SaaS - 管理员用户管理工具")
    print("="*60)

    # Check database connection
    try:
        db = SessionLocal()
        db.close()
    except Exception as e:
        print(f"\n❌ 数据库连接失败: {e}")
        print("\n请确保:")
        print("  1. 数据库服务正在运行")
        print("  2. DATABASE_URL 环境变量已正确配置")
        print("  3. 数据库迁移已完成 (alembic upgrade head)")
        return 1

    while True:
        print("\n请选择操作:")
        print("  1. 创建新管理员用户")
        print("  2. 提升现有用户为管理员")
        print("  3. 查看当前管理员列表")
        print("  4. 退出")

        choice = input("\n请输入选项 (1-4): ").strip()

        if choice == '1':
            create_new_admin()
        elif choice == '2':
            promote_existing_user()
        elif choice == '3':
            list_admins()
        elif choice == '4':
            print("\n再见!")
            return 0
        else:
            print("❌ 无效选项，请重新输入")

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
