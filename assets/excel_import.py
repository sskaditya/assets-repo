"""
Excel Import Utility for Assets
Handles importing asset data from Excel spreadsheets
"""
from openpyxl import load_workbook
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime
from decimal import Decimal
from .models import Asset, AssetCategory, AssetType, Vendor
from users.models import Location, Department


class AssetExcelImporter:
    """Handles importing assets from Excel files"""
    
    def __init__(self, file, company, user):
        self.file = file
        self.company = company
        self.user = user
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.skip_count = 0
    
    def parse_date(self, value):
        """Parse date from various formats"""
        if not value:
            return None
        
        if isinstance(value, datetime):
            return value.date()
        
        if isinstance(value, str):
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                try:
                    return datetime.strptime(value.strip(), fmt).date()
                except:
                    continue
        
        return None
    
    def parse_decimal(self, value):
        """Parse decimal from string or number"""
        if not value:
            return None
        
        try:
            if isinstance(value, str):
                # Remove currency symbols and commas
                value = value.replace('K', '').replace('$', '').replace(',', '').strip()
            return Decimal(str(value))
        except:
            return None
    
    def get_or_none(self, model, company, **kwargs):
        """Get object or return None"""
        try:
            filters = {'company': company, 'is_deleted': False}
            filters.update(kwargs)
            return model.objects.get(**filters)
        except model.DoesNotExist:
            return None
        except model.MultipleObjectsReturned:
            return model.objects.filter(**filters).first()
    
    def import_assets(self):
        """Import assets from Excel file"""
        try:
            wb = load_workbook(self.file, data_only=True)
            ws = wb.active
            
            # Expected columns (row 1)
            headers = [cell.value for cell in ws[1]]
            
            # Define expected column mapping
            expected_columns = {
                'asset_tag': ['Asset Tag', 'Tag', 'Asset ID'],
                'name': ['Asset Name', 'Name'],
                'description': ['Description'],
                'category': ['Category', 'Asset Category'],
                'asset_type': ['Type', 'Asset Type'],
                'make': ['Make', 'Manufacturer'],
                'model': ['Model'],
                'serial_number': ['Serial Number', 'Serial No', 'S/N'],
                'status': ['Status'],
                'condition': ['Condition'],
                'location': ['Location'],
                'department': ['Department'],
                'assigned_to': ['Assigned To', 'Assigned User', 'User'],
                'purchase_date': ['Purchase Date', 'PO Date'],
                'purchase_price': ['Purchase Price', 'Price', 'Cost'],
                'invoice_number': ['Invoice Number', 'Invoice No'],
                'warranty_end_date': ['Warranty End Date', 'Warranty Expiry'],
            }
            
            # Create column mapping
            col_map = {}
            for field, possible_names in expected_columns.items():
                for idx, header in enumerate(headers):
                    if header and header.strip() in possible_names:
                        col_map[field] = idx
                        break
            
            # Process each row
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    # Skip empty rows
                    if not any(row):
                        continue
                    
                    # Extract data
                    asset_tag = row[col_map.get('asset_tag', 0)] if 'asset_tag' in col_map else None
                    if not asset_tag:
                        self.errors.append(f"Row {row_idx}: Asset Tag is required")
                        self.skip_count += 1
                        continue
                    
                    # Check if asset already exists
                    if Asset.objects.filter(company=self.company, asset_tag=asset_tag, is_deleted=False).exists():
                        self.warnings.append(f"Row {row_idx}: Asset {asset_tag} already exists - skipped")
                        self.skip_count += 1
                        continue
                    
                    # Get or create related objects
                    category_name = row[col_map.get('category')] if 'category' in col_map else None
                    category = None
                    if category_name:
                        category = self.get_or_none(AssetCategory, self.company, name=category_name)
                        if not category:
                            self.warnings.append(f"Row {row_idx}: Category '{category_name}' not found - using default")
                    
                    if not category:
                        # Use first available category
                        category = AssetCategory.objects.filter(
                            company=self.company, is_deleted=False
                        ).first()
                        if not category:
                            self.errors.append(f"Row {row_idx}: No categories available in company")
                            self.skip_count += 1
                            continue
                    
                    asset_type_name = row[col_map.get('asset_type')] if 'asset_type' in col_map else None
                    asset_type = None
                    if asset_type_name:
                        asset_type = self.get_or_none(AssetType, self.company, name=asset_type_name)
                    
                    if not asset_type:
                        # Use first available type for the category
                        asset_type = AssetType.objects.filter(
                            company=self.company, category=category, is_deleted=False
                        ).first()
                        if not asset_type:
                            self.warnings.append(f"Row {row_idx}: No asset type found - using first available")
                            asset_type = AssetType.objects.filter(
                                company=self.company, is_deleted=False
                            ).first()
                    
                    if not asset_type:
                        self.errors.append(f"Row {row_idx}: No asset types available in company")
                        self.skip_count += 1
                        continue
                    
                    # Create asset
                    asset = Asset(
                        company=self.company,
                        asset_tag=str(asset_tag).strip(),
                        name=row[col_map.get('name', 1)] if 'name' in col_map else f"Asset {asset_tag}",
                        category=category,
                        asset_type=asset_type,
                    )
                    
                    # Optional fields
                    if 'description' in col_map and row[col_map['description']]:
                        asset.description = str(row[col_map['description']])
                    
                    if 'make' in col_map and row[col_map['make']]:
                        asset.make = str(row[col_map['make']])
                    
                    if 'model' in col_map and row[col_map['model']]:
                        asset.model = str(row[col_map['model']])
                    
                    if 'serial_number' in col_map and row[col_map['serial_number']]:
                        serial = str(row[col_map['serial_number']]).strip()
                        # Check for duplicate serial number
                        if Asset.objects.filter(serial_number=serial, is_deleted=False).exists():
                            self.warnings.append(f"Row {row_idx}: Serial number {serial} already exists - left blank")
                        else:
                            asset.serial_number = serial
                    
                    if 'status' in col_map and row[col_map['status']]:
                        status = str(row[col_map['status']]).strip().upper().replace(' ', '_')
                        valid_statuses = [s[0] for s in Asset.STATUS_CHOICES]
                        if status in valid_statuses:
                            asset.status = status
                    
                    if 'condition' in col_map and row[col_map['condition']]:
                        condition = str(row[col_map['condition']]).strip().upper().replace(' ', '_')
                        valid_conditions = [c[0] for c in Asset.CONDITION_CHOICES]
                        if condition in valid_conditions:
                            asset.condition = condition
                    
                    # Location
                    if 'location' in col_map and row[col_map['location']]:
                        location = self.get_or_none(Location, self.company, name=str(row[col_map['location']]))
                        if location:
                            asset.location = location
                    
                    # Department
                    if 'department' in col_map and row[col_map['department']]:
                        department = self.get_or_none(Department, self.company, name=str(row[col_map['department']]))
                        if department:
                            asset.department = department
                    
                    # Assigned user (by username or email)
                    if 'assigned_to' in col_map and row[col_map['assigned_to']]:
                        user_identifier = str(row[col_map['assigned_to']]).strip()
                        try:
                            assigned_user = User.objects.filter(
                                Q(username=user_identifier) | Q(email=user_identifier),
                                profile__company=self.company,
                                is_active=True
                            ).first()
                            if assigned_user:
                                asset.assigned_to = assigned_user
                        except:
                            pass
                    
                    # Financial fields
                    if 'purchase_date' in col_map:
                        asset.purchase_date = self.parse_date(row[col_map['purchase_date']])
                    
                    if 'purchase_price' in col_map:
                        asset.purchase_price = self.parse_decimal(row[col_map['purchase_price']])
                    
                    if 'invoice_number' in col_map and row[col_map['invoice_number']]:
                        asset.invoice_number = str(row[col_map['invoice_number']])
                    
                    if 'warranty_end_date' in col_map:
                        asset.warranty_end_date = self.parse_date(row[col_map['warranty_end_date']])
                    
                    # Save asset
                    asset.save()
                    
                    # Create history entry
                    from .models import AssetHistory
                    AssetHistory.objects.create(
                        asset=asset,
                        action_type='CREATED',
                        performed_by=self.user,
                        remarks=f'Asset imported from Excel'
                    )
                    
                    self.success_count += 1
                    
                except Exception as e:
                    self.errors.append(f"Row {row_idx}: {str(e)}")
                    self.skip_count += 1
            
            return {
                'success': self.success_count > 0,
                'success_count': self.success_count,
                'skip_count': self.skip_count,
                'errors': self.errors,
                'warnings': self.warnings,
            }
            
        except Exception as e:
            return {
                'success': False,
                'success_count': 0,
                'skip_count': 0,
                'errors': [f"File processing error: {str(e)}"],
                'warnings': [],
            }


def generate_import_template():
    """Generate an Excel template for asset import"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from io import BytesIO
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Asset Import Template"
    
    # Define headers
    headers = [
        'Asset Tag', 'Asset Name', 'Description', 'Category', 'Asset Type',
        'Make', 'Model', 'Serial Number', 'Status', 'Condition',
        'Location', 'Department', 'Assigned To',
        'Purchase Date', 'Purchase Price', 'Invoice Number', 'Warranty End Date'
    ]
    
    # Style headers
    header_fill = PatternFill(start_color="C17845", end_color="C17845", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Add example data
    example_data = [
        ['AST-001', 'Dell Laptop', 'High performance laptop', 'IT Equipment', 'Laptop',
         'Dell', 'Latitude 5520', 'SN123456', 'DEPLOYED', 'GOOD',
         'Head Office', 'IT Department', 'john.doe', '2024-01-15', '1500.00', 'INV-001', '2026-01-15'],
        ['AST-002', 'Office Chair', 'Ergonomic office chair', 'Furniture', 'Chair',
         'Herman Miller', 'Aeron', '', 'IN_USE', 'EXCELLENT',
         'Head Office', 'Admin', '', '2024-02-10', '800.00', 'INV-002', ''],
    ]
    
    for row_idx, row_data in enumerate(example_data, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)
    
    # Add instructions sheet
    ws_instructions = wb.create_sheet("Instructions")
    instructions = [
        ["Asset Import Instructions", ""],
        ["", ""],
        ["Required Fields:", ""],
        ["- Asset Tag", "Unique identifier for the asset (e.g., AST-001)"],
        ["- Asset Name", "Descriptive name of the asset"],
        ["- Category", "Must match an existing category name exactly"],
        ["- Asset Type", "Must match an existing asset type name exactly"],
        ["", ""],
        ["Optional Fields:", ""],
        ["- Description", "Detailed description of the asset"],
        ["- Make/Model", "Manufacturer and model information"],
        ["- Serial Number", "Must be unique across all assets"],
        ["- Status", "One of: PLANNING, ORDERED, IN_STOCK, DEPLOYED, IN_USE, UNDER_MAINTENANCE, RETIRED, DISPOSED"],
        ["- Condition", "One of: EXCELLENT, GOOD, FAIR, POOR, NOT_WORKING"],
        ["- Location", "Must match an existing location name"],
        ["- Department", "Must match an existing department name"],
        ["- Assigned To", "Username or email of the user"],
        ["- Purchase Date", "Format: YYYY-MM-DD or DD/MM/YYYY"],
        ["- Purchase Price", "Numeric value (e.g., 1500.00)"],
        ["- Invoice Number", "Invoice reference"],
        ["- Warranty End Date", "Format: YYYY-MM-DD or DD/MM/YYYY"],
        ["", ""],
        ["Important Notes:", ""],
        ["1. The first row must contain column headers", ""],
        ["2. Asset Tag must be unique within your company", ""],
        ["3. Category and Asset Type must exist before import", ""],
        ["4. Duplicate serial numbers will be skipped", ""],
        ["5. Invalid dates or numbers will be ignored", ""],
        ["6. Delete example data rows before importing your data", ""],
    ]
    
    for row_idx, (instruction, detail) in enumerate(instructions, start=1):
        ws_instructions.cell(row=row_idx, column=1, value=instruction)
        ws_instructions.cell(row=row_idx, column=2, value=detail)
        if instruction and "Instructions" in instruction:
            ws_instructions.cell(row=row_idx, column=1).font = Font(bold=True, size=14)
        elif instruction and ":" in instruction:
            ws_instructions.cell(row=row_idx, column=1).font = Font(bold=True)
    
    ws_instructions.column_dimensions['A'].width = 25
    ws_instructions.column_dimensions['B'].width = 60
    
    # Adjust column widths in main sheet
    for col_idx in range(1, len(headers) + 1):
        ws.column_dimensions[chr(64 + col_idx)].width = 18
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output
