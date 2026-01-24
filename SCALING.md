# Scaling fstat - Financial Agent

## Current Architecture (v0)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│   MongoDB   │
│  (React/TS) │     │  (FastAPI)  │     │             │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Anthropic   │
                   │    API      │
                   └─────────────┘
```

**Current Capacity:** ~100 concurrent users

---

## Scaling Bottlenecks

### 1. Anthropic API Rate Limits

| Tier | Requests/min | Tokens/min |
|------|-------------|------------|
| Free | 5 | 20,000 |
| Build | 50 | 40,000 |
| Scale | 1,000 | 80,000 |

**Impact:** At 500+ users submitting expenses simultaneously, you'll hit rate limits.

**Solutions:**
- Implement request queuing (Redis + Celery/ARQ)
- Add retry logic with exponential backoff
- Cache common parsing patterns
- Consider multiple API keys for load distribution

### 2. Synchronous LLM Processing

**Current Flow:**
```
User Request → Parse (LLM ~1-3s) → Validate (LLM ~1-2s) → DB Write → Response
Total: 3-6 seconds blocking
```

**Impact:** Each request holds a worker for 3-6 seconds. 10 workers = max 100-200 req/min.

**Solutions:**
- Background job processing (Celery/ARQ)
- Return job ID immediately, poll for results
- WebSocket notifications when complete
- Optimistic UI updates on frontend

### 3. Database Connections

**Current:** Default MongoDB connection pooling

**At Scale Issues:**
- Connection exhaustion
- Slow queries blocking pool
- No read replicas

**Solutions:**
```python
# Recommended MongoDB settings for scale
client = AsyncIOMotorClient(
    MONGO_URI,
    maxPoolSize=100,
    minPoolSize=10,
    maxIdleTimeMS=30000,
    waitQueueTimeoutMS=5000,
)
```

- Add indexes on frequently queried fields
- Implement read replicas for analytics
- Consider sharding for 1M+ documents

### 4. Single Server Limits

**Solutions:**
- Kubernetes/Docker Swarm for orchestration
- Load balancer (nginx, HAProxy, or cloud LB)
- Stateless backend design (already done with JWT)
- Shared session store if needed (Redis)

---

## Scaling Phases

### Phase 1: MVP (Current) - Up to 100 users
```
Request → Agent → LLM → DB → Response
```
- Single server deployment
- Direct LLM calls
- Basic error handling

### Phase 2: Growth - 100 to 1,000 users
```
Request → Redis Queue → Return Job ID
              ↓
       Celery Worker → LLM → DB
              ↓
       Notify (polling/WebSocket)
```
- Add Redis for job queuing
- Background workers for LLM calls
- Implement job status endpoints
- Add basic caching

### Phase 3: Scale - 1,000 to 10,000 users
```
                    ┌─────────────┐
                    │ Load        │
                    │ Balancer    │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Backend 1  │ │  Backend 2  │ │  Backend 3  │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           └───────────────┼───────────────┘
                          ▼
                   ┌─────────────┐
                   │    Redis    │
                   │   Cluster   │
                   └──────┬──────┘
                          ▼
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Worker 1   │ │  Worker 2   │ │  Worker N   │
    └─────────────┘ └─────────────┘ └─────────────┘
```
- Multiple backend instances
- Redis cluster for queues and caching
- Worker pool auto-scaling
- MongoDB replica set

### Phase 4: Enterprise - 10,000+ users
- Multi-region deployment
- CDN for static assets
- Database sharding
- Dedicated LLM infrastructure or fine-tuned models
- Kubernetes with HPA

---

## Implementation Priorities

### Immediate (Before 100 users)
- [ ] Add proper error handling and retries for LLM calls
- [ ] Implement request timeouts
- [ ] Add health check endpoints
- [ ] Set up logging and monitoring (Sentry, Datadog)
- [ ] Database indexes

### Short-term (100-500 users)
- [ ] Add Redis for caching
- [ ] Implement background job processing
- [ ] Add rate limiting per user
- [ ] Set up horizontal scaling infrastructure

### Medium-term (500-5000 users)
- [ ] WebSocket for real-time updates
- [ ] Read replicas for analytics
- [ ] Implement caching layer for LLM responses
- [ ] Auto-scaling workers

---

## Monitoring Checklist

### Metrics to Track
- Request latency (p50, p95, p99)
- LLM API response times
- Queue depth and processing time
- Database query performance
- Error rates by endpoint
- Active users and concurrent connections

### Alerts to Set
- API error rate > 1%
- p95 latency > 5 seconds
- Queue depth > 100 jobs
- Database connection pool > 80%
- LLM API rate limit warnings

---

## Cost Considerations

| Component | Free Tier | Growth | Scale |
|-----------|-----------|--------|-------|
| Anthropic API | $5/month | $50-200/month | $500+/month |
| MongoDB Atlas | Free (512MB) | $57/month | $200+/month |
| Redis | - | $15/month | $50+/month |
| Server (Railway/Fly) | $5/month | $20/month | $100+/month |
| **Total** | ~$10/month | ~$150/month | ~$850+/month |

---

## Quick Wins for Performance

1. **Add LLM response caching** - Many expense descriptions are similar
2. **Batch similar requests** - Group parsing requests
3. **Optimize prompts** - Shorter prompts = faster responses
4. **Use Haiku for validation** - Cheaper and faster for simple checks
5. **Implement connection pooling** - Reuse HTTP connections to Anthropic
