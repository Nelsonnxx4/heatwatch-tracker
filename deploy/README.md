# HeatWatch on one EC2 instance

This deployment runs the complete application with Docker Compose:

- Caddy is the only public container and terminates HTTPS.
- Next.js serves the dashboard and its restricted API proxy.
- FastAPI and PostgreSQL are reachable only on the private Docker network.
- The ingestion container refreshes Open-Meteo observations every hour.

This is intended for an initial portfolio or low-traffic deployment. Use ECS and
RDS when independent scaling, multi-instance availability, or managed database
backups become requirements.

## 1. Prepare secrets locally

Copy the example without committing the result:

```powershell
Copy-Item deploy/.env.production.example deploy/.env.production
```

Generate two different URL-safe secrets and place them in `POSTGRES_PASSWORD`
and `API_KEY`:

```powershell
$bytes = [byte[]]::new(32)
[Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
[Convert]::ToHexString($bytes).ToLower()
```

Keep the password hexadecimal because it is interpolated into the PostgreSQL
connection URL. Never copy values from `backend/.env` or `frontend/.env.local`
into Git.

For an IP-only first deployment, set:

```dotenv
SITE_ADDRESS=:80
SITE_ORIGIN=http://YOUR_EC2_PUBLIC_IP
```

For a real domain, point its DNS `A` record to the instance and use:

```dotenv
SITE_ADDRESS=weather.example.com
SITE_ORIGIN=https://weather.example.com
```

Caddy obtains and renews the TLS certificate after DNS resolves and inbound
ports 80 and 443 are open.

## 2. Validate and build

```powershell
docker compose --env-file deploy/.env.production `
  -f deploy/docker-compose.prod.yml config

docker compose --env-file deploy/.env.production `
  -f deploy/docker-compose.prod.yml build
```

## 3. EC2 requirements

Create the instance in the account's home Region, `eu-north-1`, with:

- a current Ubuntu or Amazon Linux AMI;
- at least 2 vCPU and 4 GiB RAM when building the images on the instance;
- an encrypted gp3 EBS root volume and a separate encrypted EBS data volume;
- IMDSv2 required with a metadata response hop limit of 2 for containers;
- an instance profile containing `AmazonSSMManagedInstanceCore`;
- a security group allowing inbound TCP 80 and 443 from the internet;
- no inbound SSH rule; use Systems Manager Session Manager instead.

Attach a stable Elastic IP only if the domain must survive instance stop/start.
AWS bills public IPv4 addresses, including Elastic IPs.

Mount the data volume at `/srv/heatwatch-data`, then set this on the instance:

```dotenv
DATA_ROOT=/srv/heatwatch-data
```

The PostgreSQL database and Caddy certificates will then survive container
recreation. Back up the data separately because a single EBS volume is not a
complete disaster-recovery strategy.

## 4. Start the application

Install Docker Engine, the Docker Compose plugin, and Git on the instance. Clone
or securely upload the repository into `/opt/heatwatch`, create
`deploy/.env.production` with permissions `600`, and run:

```bash
cd /opt/heatwatch
chmod 600 deploy/.env.production
docker compose --env-file deploy/.env.production \
  -f deploy/docker-compose.prod.yml up --build -d
```

Watch startup and the initial city ingestion:

```bash
docker compose --env-file deploy/.env.production \
  -f deploy/docker-compose.prod.yml ps

docker compose --env-file deploy/.env.production \
  -f deploy/docker-compose.prod.yml logs -f --tail=100
```

Verify the public proxy without exposing the backend:

```bash
curl --fail http://127.0.0.1/healthz
```

## 5. Back up PostgreSQL

Create a database dump on the instance and immediately move it to encrypted,
access-controlled storage such as S3:

```bash
docker compose --env-file deploy/.env.production \
  -f deploy/docker-compose.prod.yml exec -T db \
  pg_dump -U heatwatch -d heatwatch > heatwatch-$(date +%F).sql
```

Database dumps contain application data and should not remain unencrypted on
the instance.

## 6. Update

After pulling or uploading a new release:

```bash
docker compose --env-file deploy/.env.production \
  -f deploy/docker-compose.prod.yml up --build -d --remove-orphans

docker image prune -f
```

Do not run `docker compose down -v`; `-v` deletes named volumes and is unsafe for
database deployments.
