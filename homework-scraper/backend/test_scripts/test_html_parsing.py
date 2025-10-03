"""
Test HTML parsing with the provided HTML samples
"""
from bs4 import BeautifulSoup
import re

# Manodienynas HTML sample
manodienynas_html = """
<div class="md-block">
    <table class="classhomework_table fullWidth hoverTr">
        <tbody><tr>
            <th>Pamokos data</th>
            <th>Pamoka</th>
            <th>Mokytojas</th>
            <th>Namų darbas</th>
            <th class="fixed-date">Atlikti iki</th>
            <th class="fixed-date">Įvesta</th>
            <th class="fixed-attachment">Prikabinti failai</th>
        </tr>
        
        <tr class="simple_info_block stripe">
            <td>
                Rugsėjo<br>
                <div class="month_day">30</div>
                Antradienis
            </td>
            <td class="mark_subject" data-lesson-id="72">Lietuvių kalba ir literatūra</td>
            <td>Solveiga Laučienė</td>
            <td class="chDescription"><p>Darbas su pratybomis (J. Tumo-Vaižganto apysakos „Dėdės ir dėdienės" fragmentų analizė pagal nurodytus klausimus).</p></td>
            <td>2025-10-03</td>
            <td>2025-09-30</td>
            <td></td>
        </tr>
        
        <tr class="simple_info_block">
            <td>
                Rugsėjo<br>
                <div class="month_day">26</div>
                Penktadienis
            </td>
            <td class="mark_subject" data-lesson-id="52897">Matematikos modulis (dalyko modulis)</td>
            <td>Ingrida Bakutienė</td>
            <td class="chDescription"><p>41psl. 17-20 užbaigti, 20psl. 32</p></td>
            <td>2025-10-03</td>
            <td>2025-09-26</td>
            <td></td>
        </tr>
        
        <tr class="simple_info_block stripe">
            <td>
                Spalio<br>
                <div class="month_day">2</div>
                Ketvirtadienis
            </td>
            <td class="mark_subject" data-lesson-id="20">Matematika</td>
            <td>Ingrida Bakutienė</td>
            <td class="chDescription"><p>53psl. 6-8 užbaigti</p></td>
            <td>2025-10-06</td>
            <td>2025-10-02</td>
            <td></td>
        </tr>
        
        <tr class="adnet_main">
            <td colspan="100%"><!-- ads --></td>
        </tr>
    </tbody></table>
</div>
"""

# Eduka HTML sample
eduka_html = """
<div class="assignments-page">
    <div class="group-card__container" style="background-color: rgb(209, 183, 252); color: rgb(51, 51, 51);">
        <div class="group-card__title">4H</div>
        <div class="group-card__description">
            <div class="group-card__description-line">Ingrida Bakutienė</div>
            <div class="group-card__description-line">Matematika</div>
            <div class="group-card__description-line">Kauno „Saulės" gimnazija</div>
        </div>
    </div>

    <div class="assignment-list__item">
        <div class="assignment-list__cell-group">
            <app-description class="assignment-list__cell assignment-list__cell--title">
                <div class="assignment">
                    <div class="assignment__icon">
                        <app-assignment-type-icon>
                            <app-icon><i class="icon tst-icon icon--curated"></i></app-icon>
                        </app-assignment-type-icon>
                    </div>
                    <div class="assignment__description">
                        <div class="assignment__description-title tst-assignment__description-title">Trigonometrinių lygčių sprendimas</div>
                        <div class="assignment__description-tasks-count tst-assignment__description-tasks-count">15 užd.</div>
                    </div>
                </div>
            </app-description>
            <div class="assignment-list__cell assignment-list__cell--deadline">
                <span class="assignment-list__deadline-title">Atlikti iki</span>
                <span class="assignment-list__deadline-label tst-assignment-list__deadline-label">Neribotas</span>
            </div>
            <div class="assignment-list__cell assignment-list__cell--status">
                <span class="assignment-list__status-title">Statusas</span>
                <span class="assignment-list__status-label tst-assignment-list__status-label">Nepradėta</span>
            </div>
        </div>
        <div class="assignment-list__cell assignment-list__cell--actions">
            <button class="assignment-list__action-button tst-assignment-list__action-button btn btn--custom-primary">Atlikti</button>
        </div>
    </div>
</div>
"""

def test_manodienynas_parsing():
    print("\n" + "="*60)
    print("TESTING MANODIENYNAS HTML PARSING")
    print("="*60)
    
    soup = BeautifulSoup(manodienynas_html, 'html.parser')
    
    # Find homework table
    homework_table = soup.find('table', class_='classhomework_table')
    print(f"✓ Found homework table: {homework_table is not None}")
    
    if homework_table:
        tbody = homework_table.find('tbody')
        all_rows = tbody.find_all('tr') if tbody else homework_table.find_all('tr')
        print(f"✓ Found {len(all_rows)} total rows")
        
        homework_rows = []
        for row in all_rows:
            # Skip header rows
            if row.find('th'):
                continue
            
            # Skip ad rows
            row_class = row.get('class', [])
            row_class_str = ' '.join(row_class) if isinstance(row_class, list) else str(row_class)
            if 'adnet' in row_class_str.lower():
                continue
            
            # Include rows with 'simple_info_block' class
            if 'simple_info_block' in row_class_str:
                homework_rows.append(row)
        
        print(f"✓ Found {len(homework_rows)} valid homework rows")
        
        # Parse each row
        for idx, row in enumerate(homework_rows):
            cells = row.find_all('td')
            print(f"\n--- Row {idx + 1} ---")
            print(f"  Cells: {len(cells)}")
            
            if len(cells) >= 5:
                # Lesson date
                lesson_date_cell = cells[0]
                month_day_div = lesson_date_cell.find('div', class_='month_day')
                if month_day_div:
                    day = month_day_div.get_text(strip=True)
                    cell_text = lesson_date_cell.get_text('\n', strip=True).split('\n')
                    month = cell_text[0] if len(cell_text) > 0 else ""
                    weekday = cell_text[2] if len(cell_text) > 2 else ""
                    lesson_date = f"{month} {day}, {weekday}"
                else:
                    lesson_date = lesson_date_cell.get_text(strip=True)
                print(f"  Lesson date: {lesson_date}")
                
                # Subject
                subject = cells[1].get_text(strip=True)
                print(f"  Subject: {subject}")
                
                # Teacher
                teacher = cells[2].get_text(strip=True)
                print(f"  Teacher: {teacher}")
                
                # Description
                desc_cell = cells[3]
                desc_p = desc_cell.find('p')
                description = desc_p.get_text(strip=True) if desc_p else desc_cell.get_text(strip=True)
                print(f"  Description: {description[:50]}...")
                
                # Due date
                due_date_text = cells[4].get_text(strip=True)
                print(f"  Due date: {due_date_text}")

def test_eduka_parsing():
    print("\n" + "="*60)
    print("TESTING EDUKA HTML PARSING")
    print("="*60)
    
    soup = BeautifulSoup(eduka_html, 'html.parser')
    
    # Extract group name
    group_desc_lines = soup.find_all(class_='group-card__description-line')
    if len(group_desc_lines) >= 2:
        group_name = group_desc_lines[1].get_text(strip=True)
        print(f"✓ Group name: {group_name}")
    
    # Find assignment items
    assignment_items = soup.find_all(class_='assignment-list__item')
    print(f"✓ Found {len(assignment_items)} assignment items")
    
    for idx, item in enumerate(assignment_items):
        print(f"\n--- Assignment {idx + 1} ---")
        
        # Title
        title_elem = item.find(class_='assignment__description-title')
        if title_elem:
            title = title_elem.get_text(strip=True)
            print(f"  Title: {title}")
        
        # Task count
        task_count_elem = item.find(class_='assignment__description-tasks-count')
        if task_count_elem:
            task_count = task_count_elem.get_text(strip=True)
            print(f"  Task count: {task_count}")
        
        # Deadline
        deadline_elem = item.find(class_='assignment-list__deadline-label')
        if deadline_elem:
            deadline = deadline_elem.get_text(strip=True)
            print(f"  Deadline: {deadline}")
        
        # Status
        status_elem = item.find(class_='assignment-list__status-label')
        if status_elem:
            status = status_elem.get_text(strip=True)
            print(f"  Status: {status}")

if __name__ == '__main__':
    test_manodienynas_parsing()
    test_eduka_parsing()
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
