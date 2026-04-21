import flet as ft
import math

def main(page: ft.Page):
    # 아쉬워하셨던 앱 제목과 페이지 설정
    page.title = "U-Boat Fire Control System v1.2"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    # 화면 중앙 정렬 설정
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    # --- 입력창 생성 함수 (디자인 개선) ---
    def create_input(label_text):
        return ft.TextField(
            label=label_text,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color="bluegrey700",
            focused_border_color="blue400", # 포커스 시 색상 변경
            height=60, # 입력창 높이 확보
        )

    dist1_input = create_input("1차 거리 (m)")
    bear1_input = create_input("1차 방위 (deg)")
    time_input = create_input("시간 간격 (sec)")
    dist2_input = create_input("2차 거리 (m)")
    bear2_input = create_input("2차 방위 (deg)")
    
    target_len_input = ft.TextField(
        label="목표 함선 길이 (m)", 
        value="150", 
        visible=False,
        text_align=ft.TextAlign.CENTER
    )
    salvo_count_input = ft.Slider(
        min=2, max=4, divisions=2, 
        label="사격 발수: {value}발", 
        visible=False
    )
    
    result_display = ft.Text(
        value="데이터를 입력하고 FIRE!를 누르세요", 
        size=18, 
        color="amber", 
        weight="bold",
        text_align=ft.TextAlign.CENTER
    )

    # --- 모드 변경 핸들러 ---
    def on_mode_change(e):
        if aft_switch.value:
            salvo_switch.value = False
            salvo_switch.disabled = True
        else:
            salvo_switch.disabled = False
            
        target_len_input.visible = salvo_switch.value
        salvo_count_input.visible = salvo_switch.value
        page.update()

    aft_switch = ft.Switch(label="후방(Tube 5)", on_change=on_mode_change)
    salvo_switch = ft.Switch(label="Salvo 모드", on_change=on_mode_change)

    # --- 계산 함수 ---
    def calculate(e):
        try:
            d1 = float(dist1_input.value)
            b1 = float(bear1_input.value)
            t = float(time_input.value)
            d2 = float(dist2_input.value)
            b2 = float(bear2_input.value)

            r1, r2 = math.radians(b1), math.radians(b2)
            x1, y1 = d1 * math.sin(r1), d1 * math.cos(r1)
            x2, y2 = d2 * math.sin(r2), d2 * math.cos(r2)

            dist_moved = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            speed = (dist_moved / t) * 1.94384 if t > 0 else 0
            course = math.degrees(math.atan2(x2-x1, y2-y1))
            if course < 0: course += 360

            aob_val = course - b2
            
            if aft_switch.value:
                aob_val -= 180

            while aob_val > 180: aob_val -= 360
            while aob_val < -180: aob_val += 360
            
            final_aob = 180 - abs(aob_val)
            side = "우현(Starboard)" if aob_val >= 0 else "좌현(Port)"

            output = f"▶ 속도: {speed:.2f} kts\n▶ 침로: {course:.1f}°\n▶ AoB: {final_aob:.1f}° ({side})"

            if salvo_switch.value and not aft_switch.value:
                t_len = float(target_len_input.value)
                apparent_len = t_len * math.sin(math.radians(final_aob))
                total_spread = math.degrees(math.atan(apparent_len / d2)) if d2 > 0 else 0
                num_torp = int(salvo_count_input.value)
                interval = total_spread / (num_torp - 1) if num_torp > 1 else 0
                output += f"\n\n[SALVO 정보]\n전체 확산각: {total_spread:.1f}°\n발당 간격: {interval:.1f}°"

            result_display.value = output
        except Exception:
            result_display.value = "입력 오류: 숫자를 확인하세요"
        
        page.update()

    # --- 화면 구성 (레이아웃 개선) ---
    # 전체를 감싸는 컨테이너로 여백과 중앙 배치를 조절합니다.
    layout = ft.Container(
        content=ft.Column(
            [
                ft.Text("7C Fire Control Computer", size=28, weight="bold", color="bluegrey100"),
                ft.Divider(height=10, color="bluegrey800"),
                
                # 스위치 영역
                ft.Row([aft_switch, salvo_switch], alignment=ft.MainAxisAlignment.CENTER),
                
                # 입력창 영역 (spacing으로 간격 확보)
                ft.Column([
                    dist1_input, bear1_input, time_input, dist2_input, bear2_input,
                    target_len_input,
                    salvo_count_input,
                ], spacing=15), 
                
                # 버튼 영역
                ft.ElevatedButton(
                    content=ft.Text("계산 실행 (FIRE!)", color="white", size=20, weight="bold"),
                    on_click=calculate,
                    width=400,
                    height=65,
                    style=ft.ButtonStyle(
                        bgcolor="red900", 
                        shape=ft.RoundedRectangleBorder(radius=12)
                    )
                ),
                
                # 결과 출력 영역
                ft.Container(
                    content=result_display,
                    padding=20,
                    bgcolor="grey950",
                    border=ft.border.all(1, "bluegrey800"),
                    border_radius=15,
                    width=400
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25 # 섹션 간의 간격
        ),
        padding=ft.padding.only(top=20, bottom=40), # 상하 패딩으로 여유공간 확보
    )

    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)
