# test-reservation-system

## 요구 사항
### 공통
- [x] 회원가입
- [x] 로그인

### admin
- [x] 전체 예약 조회 api
- [x] 특정 예약 확정 api
  - [x] 존재하지 않은 예약 id 확정 요청 시 예외처리
  - [x] 이미 확정된 예약을 중복해서 확정하려고 할 시 예외처리
  - [x] 확정하고자 하는 예약의 인원 수 + 같은 시간대를 포함하는 이미 확정된 예약들의 총 인원 수 > 50,000이면 예외처리
- [x] 특정 예약 삭제 api
  - [x] 존재하지 않는 예약 id 삭제 요청 시 예외처리

### user
- [x] 자신이 등록한 예약들 조회 api
- [ ] 자신의 예약을 삭제 api
  - [ ] 존재하지 않은 예약 id로 삭제 요청 시 예외처리
  - [ ] 다른 사람이 작성한 예약 삭제 요청 시 예외처리
  - [ ] 이미 확정된 예약 삭제 요청 시 예외처리
