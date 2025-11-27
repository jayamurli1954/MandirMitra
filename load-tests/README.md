# Load Testing for MandirSync with Locust

This directory contains load testing scripts using Locust to simulate concurrent users and measure system performance.

## Installation

```bash
cd load-tests
pip install -r requirements.txt
```

## Running Load Tests

### Basic Usage

```bash
locust -f locustfile.py --host=http://localhost:8000
```

Then open http://localhost:8089 in your browser to access the Locust web UI.

### Command Line Mode (No Web UI)

```bash
locust -f locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 2 --run-time 5m --headless
```

## Test Scenarios

### 1. Normal Day (10 users)
Simulates normal temple operations with 2-3 counters active.

```bash
locust -f locustfile.py --users 10 --spawn-rate 2 --run-time 10m
```

**Expected Performance:**
- Response time: < 200ms (95th percentile)
- RPS: 20-30 requests/second
- Failure rate: < 1%

### 2. Festival Day (50 users)
Simulates heavy load during festivals with multiple counters.

```bash
locust -f locustfile.py --users 50 --spawn-rate 10 --run-time 10m
```

**Expected Performance:**
- Response time: < 500ms (95th percentile)
- RPS: 100-150 requests/second
- Failure rate: < 2%

### 3. Stress Test (100 users)
Tests system limits to identify breaking point.

```bash
locust -f locustfile.py --users 100 --spawn-rate 20 --run-time 10m
```

**Watch for:**
- Increased error rates
- Response time degradation
- Database connection pool exhaustion

### 4. Spike Test
Sudden traffic increase scenario.

1. Start with 10 users
2. After 2 minutes, increase to 100 users rapidly
3. Monitor system behavior during spike

## User Classes

### DonationUser
Simulates counter staff recording donations.
- **Tasks**: Record donation (60%), List donations (25%), View details (10%), Generate receipt (5%)
- **Wait time**: 1-3 seconds between tasks

### SevaBookingUser
Simulates counter staff booking sevas.
- **Tasks**: Book seva (50%), List sevas (25%), View bookings (20%), Check availability (5%)
- **Wait time**: 2-5 seconds between tasks

### AdminUser
Simulates admin users accessing reports.
- **Tasks**: View dashboard (30%), Trial balance (25%), Chart of accounts (20%), Employee list (15%), Income statement (10%)
- **Wait time**: 5-10 seconds between tasks

### MixedWorkloadUser
Realistic mix of donation (60%) and seva (40%) operations.

## Metrics to Monitor

### Response Times
- **Good**: < 200ms median, < 500ms 95th percentile
- **Acceptable**: < 500ms median, < 1000ms 95th percentile
- **Poor**: > 1000ms median

### Requests Per Second (RPS)
- **10 users**: 20-30 RPS
- **50 users**: 100-150 RPS
- **100 users**: 200-300 RPS

### Failure Rate
- **Good**: < 1%
- **Acceptable**: < 5%
- **Critical**: > 10%

## Interpreting Results

### Response Time Distribution
Check percentiles in Locust UI:
- **50th percentile (median)**: Half of requests faster than this
- **95th percentile**: 95% of requests faster than this
- **99th percentile**: Critical for worst-case scenarios

### Common Issues

#### High response times (> 1s)
**Possible causes:**
- Database query optimization needed
- Connection pool too small
- Insufficient server resources

**Solutions:**
- Add database indexes
- Increase connection pool size (default 5 → 20)
- Scale server (more CPU/RAM)

#### Connection errors
**Causes:**
- Database connection pool exhausted
- Too many open connections

**Solutions:**
```python
# backend/app/core/database.py
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,        # Increase from 5
    max_overflow=40,     # Increase from 10
    pool_pre_ping=True
)
```

#### Timeout errors
**Causes:**
- Slow API endpoints
- PDF generation blocking requests

**Solutions:**
- Use async background tasks for PDF generation
- Optimize slow database queries
- Add caching for frequently accessed data

## Production Setup

For production load testing:

```bash
# Use production-like environment
locust -f locustfile.py \
  --host=https://staging.mandirsync.org \
  --users 50 \
  --spawn-rate 10 \
  --run-time 30m \
  --html report.html
```

## Continuous Integration

Add to GitHub Actions:

```yaml
- name: Load Test
  run: |
    cd load-tests
    pip install -r requirements.txt
    locust -f locustfile.py --headless --users 20 --spawn-rate 5 --run-time 2m --host=http://localhost:8000
```

## Best Practices

1. **Start small**: Begin with 10 users, gradually increase
2. **Monitor server**: Watch CPU, memory, database connections
3. **Test regularly**: Run weekly to catch performance regressions
4. **Test different scenarios**: Normal day, festival, month-end closing
5. **Fix bottlenecks**: Address highest response time endpoints first

## Example Output

```
Type     Name                                  # reqs    # fails  Avg   Min   Max  Median  req/s
POST     /api/v1/donations/                     1234       0     145    45   890    120    12.5
GET      /api/v1/donations/ [list]              456        2     89     12   450    75     4.6
POST     /api/v1/sevas/bookings                 789        1     167    56   780    140    8.0
GET      /api/v1/accounting/reports/trial       123        0     456    120  1200   400    1.2

Aggregated                                      2602       3     165    12   1200   110    26.3
```

## Resources

- [Locust Documentation](https://docs.locust.io/)
- [FastAPI Performance](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
