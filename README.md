# 시험 일정 예약 구축하기

## 요구 사항
### 공통
- [x] 회원가입
- [x] 로그인

### admin
- [x] 전체 예약 조회 api
- [x] 특정 에약 수정 api
  - [x] 존재하지 않은 예약 id 수정 요청 시 예외처리
  - [x] 날짜 및 시간 수정을 현재보다 이전으로 수정 요청 시 예외처리
  - [x] 인원 변경 시 그 시간 대의 총 인원의 수가 50,000명을 넘을 시 예외처리
  - [x] test_end_time이 test_start_time보다 작을 시 예외처리
- [x] 특정 예약 확정 api
  - [x] 존재하지 않은 예약 id 확정 요청 시 예외처리
  - [x] 이미 확정된 예약을 중복해서 확정하려고 할 시 예외처리
  - [x] 확정하고자 하는 예약의 인원 수 + 같은 시간대를 포함하는 이미 확정된 예약들의 총 인원 수 > 50,000이면 예외처리
- [x] 특정 예약 삭제 api
  - [x] 존재하지 않는 예약 id 삭제 요청 시 예외처리

### user
- [x] 예약 생성 api
  - [x] 시험 날짜가 현재 기준 3일 이내로 예약시 예외 발생
  - [x] 예약 신청 인원 수 + 같은 시간대를 포함하는 이미 확정된 예약들의 총 인원 수 > 50,000이면 예외처리
- [x] 자신이 등록한 예약들 조회 api
- [x] 자신이 등록한 예약 수정 api
  - [x] 존재하지 않은 예약 id로 수정 요청 시 예외처리
  - [x] 다른 기업이 작성한 예약 수정 요청 시 예외처리
  - [x] 날짜 및 시간 수정을 현재 기준 3일 이내으로 수정 요청 시 예외처리
  - [x] 인원 변경 시 그 시간 대의 총 인원의 수가 50,000명을 넘을 시 예외처리
  - [x] test_end_time이 test_start_time보다 작을 시 예외처리
  - [x] 현재 확정된 예약을 수정 요청 시 예외처리
- [x] 자신의 예약을 삭제 api
  - [x] 존재하지 않은 예약 id로 삭제 요청 시 예외처리
  - [x] 다른 기업이 작성한 예약 삭제 요청 시 예외처리
  - [x] 이미 확정된 예약 삭제 요청 시 예외처리
- [x] 예약 가능한 시간대와 인원 수 조회 api
  - [x] 현재 날짜보다 이전 날짜를 입력하면 예외처리

## Api
### admin
| URL | HTTP Method | 설명 |
|-----|-------------|------|
| `/api/admin-reservation/reservations/` | `GET` | 전체 예약 목록 조회 |
| `/api/admin-reservation/{id}/update/` | `PATCH` | 특정 예약 수정 |
| `/api/admin-reservation/{id}/confirm/` | `PATCH` | 특정 예약 확정 |
| `/api/admin-reservation/{id}/delete/` | `DELETE` | 특정 예약 삭제 |

### user
| URL | HTTP Method | 설명 |
|-----|-------------|------|
| `/api/reservation/create/` | `POST` | 예약 생성 |
| `/api/reservation/my/` | `GET` | 본인의 예약 목록 조회 |
| `/api/reservation/{id}/update/` | `PATCH` | 본인의 예약 수정 |
| `/api/reservation/{id}/delete/` | `DELETE` | 본인의 예약 삭제 |
| `/api/reservation/available/?date=YYYY-MM-DD` | `GET` | 입력한 날짜 기준 시간대별 예약 가능 인원 조회 |
