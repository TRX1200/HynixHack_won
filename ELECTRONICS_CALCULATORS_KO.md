# 회로·공정 기초 계산기 6개

이 모듈은 직접 작성한 MIT 코드이며 Python 3.10 이상 표준 라이브러리만 사용합니다. 실행 중 패키지 설치·네트워크·API 키·추가 AI 호출이 없고 입력을 수정하지 않습니다. 일반 공식으로 작은 수치 예제를 검산하는 용도입니다. 실제 소자·공정의 정확도를 보장하는 SPICE/TCAD/PDK는 아니며, Cofa에서의 실행은 아직 확인하지 않았습니다.

## 시작하기

```sh
python -m workbench calculate examples/electronics/rc.json
```

또는 Python에서 `from workbench.electronics import calculate` 후 아래 객체를 전달합니다.

```json
{
  "calculator": "rc",
  "resistance_ohm": 1000,
  "capacitance_f": 0.000001
}
```

결과는 `results`, 입력 단위가 드러나는 `inputs`, 적용 조건인 `assumptions`, 사용한 `formula`를 포함합니다. 위 예제는 1 kΩ와 1 µF이므로 시간상수 0.001 s, 차단주파수 약 159.154943 Hz입니다. 각 입력 파일은 `examples/electronics/`에 있습니다.

## 단위부터 확인

JSON 숫자는 `1000`, `1e-6`처럼 입력합니다. `"1 kOhm"`, `"10nm"` 같은 문자열은 허용하지 않습니다. 없는 필드·추가 필드·bool·NaN·Infinity를 거절합니다. 저항·정전용량·길이·면적·두께·절대온도는 0보다 커야 합니다. 활성화에너지·확산계수·시간은 0 이상입니다. 전압은 방향을 나타내는 음수도 허용합니다.

| 주어진 단위 | 넣을 SI 값 |
|---|---|
| 1 kΩ | `1000` Ω |
| 1 µF / 1 nF / 1 pF | `1e-6` / `1e-9` / `1e-12` F |
| 1 nm / 1 µm / 1 cm | `1e-9` / `1e-6` / `1e-2` m |
| 1 cm² | `1e-4` m² |
| 1 Ω·cm | `1e-2` Ω·m |
| 1 cm²/s | `1e-4` m²/s |
| 섭씨 T °C | `T + 273.15` K |

에너지는 **활성화 사건 하나당 eV**, 온도는 **K**로 받습니다. J/mol과 섭씨를 그대로 넣으면 다른 문제를 계산하게 됩니다. 숫자만 보고 단위를 자동 추정하지 않습니다. `relative_permittivity`는 무차원 입력이며 재료 이름으로 값을 조회하지 않습니다.

## 계산 범위와 손계산 기준값

| calculator | 필수 입력 | 공식과 출력 | 검산 예제 |
|---|---|---|---|
| `ohm` | `voltage_v`, `resistance_ohm` | I=V/R → `current_a`; P=VI → `power_w` | 12 V, 6 Ω → 2 A, 24 W |
| `rc` | `resistance_ohm`, `capacitance_f` | τ=RC → `time_constant_s`; fc=1/(2πRC) → `cutoff_hz` | 1 kΩ, 1 µF → 1 ms, 약 159.154943 Hz |
| `parallel_plate` | `relative_permittivity`, `area_m2`, `thickness_m` | C=ε₀εrA/t → `capacitance_f` | 진공 εr=1, 1 m², 1 mm → 약 8.854187819 nF |
| `thin_film` | `resistivity_ohm_m`, `length_m`, `width_m`, `thickness_m` | Rs=ρ/t → `sheet_resistance_ohm_per_square`; R=Rs·L/W → `resistance_ohm` | ρ=1e-6 Ω·m, t=1 µm, L=1 mm, W=0.1 mm → Rs=1 Ω/□, R=10 Ω |
| `arrhenius` | `activation_energy_ev`, `temperature_1_k`, `temperature_2_k` | k(T2)/k(T1)=exp[(Ea/kB)(1/T1−1/T2)] → `rate_ratio_t2_over_t1`; 자연로그 → `log_rate_ratio` | Ea=0.5 eV, 300→600 K → 약 15842.187696배 |
| `diffusion_1d` | `diffusivity_m2_per_s`, `time_s` | RMS=√(2Dt) → `rms_displacement_m` | D=1e-14 m²/s, t=50 s → 1 µm RMS |

### 어떤 가정이 필요한가

- Ohm: 저항이 일정한 이상적인 DC 옴성 저항입니다. 자기발열·비선형 소자의 I–V는 계산하지 않습니다.
- RC: 이상적인 1차 무부하 필터입니다. fc에서 전압 크기는 통과대역의 1/√2, 약 −3.01 dB입니다. 소스/부하 임피던스와 기생성분이 있으면 식을 다시 세워야 합니다.
- 평행판: 균일한 선형 유전체가 틈을 완전히 채운다고 가정합니다. 가장자리 전계·누설·양자효과는 포함하지 않습니다.
- 박막: 균일한 직사각형, 일정한 bulk 비저항, 옴성 전도를 가정합니다. 접촉저항·고주파·크기효과는 없습니다. 면저항 단위 Ω/□는 길이 단위로 나누는 뜻이 아닙니다.
- Arrhenius: 두 온도에서 Ea와 온도에 무관한 prefactor가 같아야 합니다. 반환값은 **Arrhenius 계수의 비**이며 실제 반응 속도비에는 농도 등 다른 인자도 같아야 합니다. 수명비를 구한다면 해당 모델에서 속도와 수명의 관계부터 확인해야 합니다.
- 확산: 일정한 D, 무한한 균일 1차원 공간, 무표류·무경계 조건의 RMS 변위입니다. **접합 깊이, 평균 절대 이동거리, 최대 확산거리와 다릅니다.** 도핑 농도·배경 농도·경계 조건 없이 반도체 접합 깊이로 해석하면 안 됩니다.

부동소수점 근사 계산이며 측정 불확도·유효숫자·모델 오차를 대신 처리하지 않습니다. overflow/underflow로 유한하고 의미 있는 결과를 만들 수 없으면 `ValueError`로 실패합니다. 극단적인 입력은 계산 순서의 중간값 때문에 거절될 수 있습니다.

## 검증

```sh
python -B -S -m unittest tests.test_electronics -v
```

손계산 가능한 기준값, 독립적인 60자리 Decimal Arrhenius 기준값, 온도 교환 시 역수 관계, 같은 온도/영 활성화에너지, 면적·두께·시간 스케일, 같은 L/W의 면저항, 음수 전압, 0 시간, 잘못된 단위 필드·타입·범위, overflow/underflow, 입력 보존, 유한 JSON 출력을 검사합니다. 이 테스트가 실제 과제의 모델 선택까지 검증하는 것은 아닙니다.

## 공식·상수 근거

아래 원문에서 식과 적용 조건을 확인했습니다. 원문 교재·PDF를 준비팩에 복제하지 않았습니다.

- [OpenStax University Physics 2, 9.4 Ohm's Law](https://openstax.org/books/university-physics-volume-2/pages/9-4-ohms-law): 옴성 소자의 V=IR.
- [OpenStax 9.5 Electrical Energy and Power](https://openstax.org/books/university-physics-volume-2/pages/9-5-electrical-energy-and-power): 전력과 전압·전류 관계.
- [OpenStax 10.5 RC Circuits](https://openstax.org/books/university-physics-volume-2/pages/10-5-rc-circuits): τ=RC.
- [University of Louisville ECE252, Lesson 15](https://engineering.louisville.edu/raise/ECE252/L15.htm): ωc=1/RC, ω=2πf, 무부하 조건.
- [OpenStax 8.1 Capacitors and Capacitance](https://openstax.org/books/university-physics-volume-2/pages/8-1-capacitors-and-capacitance) 및 [8.4 Capacitor with a Dielectric](https://openstax.org/books/university-physics-volume-2/pages/8-4-capacitor-with-a-dielectric): 평행판 C=ε₀A/d, 유전체 배수.
- [OpenStax 9.3 Resistivity and Resistance](https://openstax.org/books/university-physics-volume-2/pages/9-3-resistivity-and-resistance) 및 [Wright State University EE480/680 강의, p.56](https://cecs.wright.edu/~kxue/mems/MEMS_Fabrication_M06.pdf): R=ρL/A, Rs=ρ/t, R=RsL/W.
- [Rawlings & Ekerdt, Chemical Reactor Analysis and Design Fundamentals, 식 5.37](https://sites.engineering.ucsb.edu/~jbraw/chemreacfun/CHEMREACFUN-book-2nd-edition-5th-printing.pdf): k=k₀exp(−Ea/kBT). 동일 prefactor라는 가정으로 두 식을 나누어 온도비 식을 얻었습니다.
- [MIT J. Dunkel, 18.095 강의노트, 식 1.13](https://math.mit.edu/classes/18.095/2015IAP/lecture5/Dunkel_lect_notes.pdf): 1차원 평균제곱변위 2Dt.
- [NIST CODATA 2022 상수표](https://physics.nist.gov/cuu/Constants/Table/allascii.txt): ε₀=8.8541878188e-12 F/m(측정 불확도 존재). [NIST SI 정의 상수](https://www.nist.gov/pml/special-publication-330/sp-330-section-2)의 정확한 kB=1.380649e-23 J/K와 e=1.602176634e-19 C를 나눠 kB/e≈8.617333262145e-5 eV/K를 사용합니다. 계산기는 상수의 불확도를 전파하지 않습니다.
