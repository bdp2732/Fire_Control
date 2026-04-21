import flet as ft
import math

def main(page: ft.Page):
    page.title = "U-Boat Fire Control System v1.4"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    def create_input(label_text, value="0"):
        return ft.TextField(
            label=label_text,
            value=value,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            height=60,
        )


    # 내 배 정보 (절대 속도 계산용)
    own_speed_input = create_input("내 배 속도 (kts)", "0")
    own_course_input = create_input("내 배 침로 (deg)", "0")
    
    # 관측 정보
    dist1_input = create_input("1차 거리 (m)")
    bear1_input = create_input("1차 상대방위 (deg)")
    time_input = create_input("측정 시간 (sec)")
    dist2_input = create_input("2차 거리 (m)")
    bear2_input = create_input("2차 상대방위 (deg)")

    result_display = ft.Text(value="READY TO FIRE", size=18, color="amber", weight="bold")

    def calculate(e):
        try:
            # 1. 값 읽어오기
            v_own = float(own_speed_input.value) * 0.51444  # kts -> m/s 변환
            c_own = float(own_course_input.value)
            d1, b1 = float(dist1_input.value), float(bear1_input.value)
            t = float(time_input.value)
            d2, b2 = float(dist2_input.value), float(bear2_input.value)

            # 2. 내 배의 이동 거리 계산 (t초 동안)
            own_dist_moved = v_own * t
            # 내 배의 이동 벡터 (북쪽 0도 기준)
            own_dx = own_dist_moved * math.sin(math.radians(c_own))
            own_dy = own_dist_moved * math.cos(math.radians(c_own))

            # 3. 적함의 '절대 좌표' 계산
            # 1차 측정 시 적함 위치 (내 시작점을 0,0으로 가정)
            # b1은 내 침로 기준 상대 방위이므로 절대 방위로 변환
            abs_b1 = (c_own + b1) % 360
            x1 = d1 * math.sin(math.radians(abs_b1))
            y1 = d1 * math.cos(math.radians(abs_b1))

            # 2차 측정 시 적함 위치 (내 이동 좌표 + 측정된 상대 위치)
            abs_b2 = (c_own + b2) % 360
            x2 = own_dx + d2 * math.sin(math.radians(abs_b2))
            y2 = own_dy + d2 * math.cos(math.radians(abs_b2))

            # 4. 적함의 실제 이동 거리 및 속도 산출
            target_dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            abs_speed = (target_dist / t) * 1.94384  # m/s -> kts
            abs_course = math.degrees(math.atan2(x2 - x1, y2 - y1)) % 360

            # 5. AoB 산출 (적함 침로와 내 현재 방위의 관계)
            # 사격 시점(2차 측정)의 내 위치와 적 위치 기준
            aob_val = abs_course - abs_b2
            while aob_val > 180: aob_val -= 360
            while aob_val < -180: aob_val += 360
            final_aob = 180 - abs(aob_val)
            side = "우현(STBD)" if aob_val >= 0 else "좌현(PORT)"

            result_display.value = (
                f"▶ 적 절대 속도: {abs_speed:.2f} kts\n"
                f"▶ 적 절대 침로: {abs_course:.1f}°\n"
                f"▶ 실시간 AoB: {final_aob:.1f}° ({side})"
            )
        except Exception as ex:
            result_display.value = "입력 데이터 오류"
        page.update()


    page.add(
        ft.Column([
            ft.Text("7C Fire Control v1.4 (ABSOLUTE)", size=24, weight="bold"),
            ft.Row([own_speed_input, own_course_input]), # 내 배 정보 레이아웃
            ft.Divider(),
            dist1_input, bear1_input, time_input, dist2_input, bear2_input,
            ft.ElevatedButton("FIRE! (Calculate)", on_click=calculate, width=400, height=50),
            result_display
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)
