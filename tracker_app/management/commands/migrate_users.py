from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    help = 'Migrate existing User data to CustomUser model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        try:
            from django.contrib.auth.models import User as OldUser
            old_users = OldUser.objects.all()
            
            if not old_users.exists():
                self.stdout.write(
                    self.style.SUCCESS('No old users to migrate')
                )
                return
                
            migrated_count = 0
            
            with transaction.atomic():
                for old_user in old_users:
                    try:
                        # Check if user already exists in CustomUser
                        if User.objects.filter(username=old_user.username).exists():
                            self.stdout.write(
                                self.style.WARNING(
                                    f'User {old_user.username} already exists, skipping...'
                                )
                            )
                            continue
                            
                        if not dry_run:
                            # Create new CustomUser
                            new_user = User.objects.create_user(
                                username=old_user.username,
                                email=old_user.email or f'{old_user.username}@example.com',
                                password=None,  # Will be set below
                                first_name=old_user.first_name,
                                last_name=old_user.last_name,
                                is_staff=old_user.is_staff,
                                is_active=old_user.is_active,
                                is_superuser=old_user.is_superuser,
                                date_joined=old_user.date_joined,
                                last_login=old_user.last_login,
                            )
                            
                            # Copy the hashed password directly
                            new_user.password = old_user.password
                            new_user.save()
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Migrated user: {old_user.username}'
                                )
                            )
                        else:
                            self.stdout.write(
                                f'Would migrate user: {old_user.username} ({old_user.email})'
                            )
                            
                        migrated_count += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Error migrating user {old_user.username}: {str(e)}'
                            )
                        )
                        
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully migrated {migrated_count} users'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Would migrate {migrated_count} users'
                    )
                )
                
        except ImportError:
            self.stdout.write(
                self.style.SUCCESS('No old User model found - migration not needed')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Migration failed: {str(e)}')
            )
            raise