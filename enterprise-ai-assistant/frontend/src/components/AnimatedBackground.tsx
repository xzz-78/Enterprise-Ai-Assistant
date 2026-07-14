import React, { useEffect, useRef, useCallback } from 'react'

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
  color: string
  alpha: number
}

interface GridLine {
  x1: number
  y1: number
  x2: number
  y2: number
  alpha: number
}

const AnimatedBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const particlesRef = useRef<Particle[]>([])
  const gridLinesRef = useRef<GridLine[]>([])
  const animationRef = useRef<number>(0)
  const mouseRef = useRef({ x: -1000, y: -1000 })

  const colors = [
    'rgba(99, 102, 241, ',
    'rgba(139, 92, 246, ',
    'rgba(6, 182, 212, ',
    'rgba(34, 211, 238, ',
  ]

  const initParticles = useCallback((width: number, height: number) => {
    const particles: Particle[] = []
    const count = Math.min(Math.floor((width * height) / 15000), 80)

    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1,
        color: colors[Math.floor(Math.random() * colors.length)],
        alpha: Math.random() * 0.5 + 0.2,
      })
    }

    particlesRef.current = particles
  }, [])

  const initGrid = useCallback((width: number, height: number) => {
    const lines: GridLine[] = []
    const gridSize = 60

    for (let x = 0; x <= width; x += gridSize) {
      lines.push({
        x1: x,
        y1: 0,
        x2: x,
        y2: height,
        alpha: Math.random() * 0.05 + 0.02,
      })
    }

    for (let y = 0; y <= height; y += gridSize) {
      lines.push({
        x1: 0,
        y1: y,
        x2: width,
        y2: y,
        alpha: Math.random() * 0.05 + 0.02,
      })
    }

    gridLinesRef.current = lines
  }, [])

  const draw = useCallback((ctx: CanvasRenderingContext2D, width: number, height: number) => {
    ctx.fillStyle = '#0f172a'
    ctx.fillRect(0, 0, width, height)

    gridLinesRef.current.forEach((line) => {
      ctx.beginPath()
      ctx.strokeStyle = `rgba(99, 102, 241, ${line.alpha})`
      ctx.lineWidth = 0.5
      ctx.moveTo(line.x1, line.y1)
      ctx.lineTo(line.x2, line.y2)
      ctx.stroke()
    })

    const particles = particlesRef.current

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i]

      p.x += p.vx
      p.y += p.vy

      if (p.x < 0 || p.x > width) p.vx *= -1
      if (p.y < 0 || p.y > height) p.vy *= -1

      const dx = mouseRef.current.x - p.x
      const dy = mouseRef.current.y - p.y
      const dist = Math.sqrt(dx * dx + dy * dy)

      if (dist < 150) {
        p.vx -= dx * 0.0005
        p.vy -= dy * 0.0005
      }

      ctx.beginPath()
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
      ctx.fillStyle = p.color + p.alpha + ')'
      ctx.fill()

      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j]
        const dx2 = p.x - p2.x
        const dy2 = p.y - p2.y
        const dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2)

        if (dist2 < 120) {
          ctx.beginPath()
          ctx.strokeStyle = p.color + (1 - dist2 / 120) * 0.15 + ')'
          ctx.lineWidth = 0.5
          ctx.moveTo(p.x, p.y)
          ctx.lineTo(p2.x, p2.y)
          ctx.stroke()
        }
      }
    }

    if (mouseRef.current.x > 0 && mouseRef.current.y > 0) {
      const gradient = ctx.createRadialGradient(
        mouseRef.current.x,
        mouseRef.current.y,
        0,
        mouseRef.current.x,
        mouseRef.current.y,
        150
      )
      gradient.addColorStop(0, 'rgba(99, 102, 241, 0.05)')
      gradient.addColorStop(1, 'rgba(99, 102, 241, 0)')
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, width, height)
    }
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      initParticles(canvas.width, canvas.height)
      initGrid(canvas.width, canvas.height)
    }

    resize()
    window.addEventListener('resize', resize)

    const animate = () => {
      draw(ctx, canvas.width, canvas.height)
      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY }
    }

    const handleMouseLeave = () => {
      mouseRef.current = { x: -1000, y: -1000 }
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      window.removeEventListener('resize', resize)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseleave', handleMouseLeave)
      cancelAnimationFrame(animationRef.current)
    }
  }, [initParticles, initGrid, draw])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ opacity: 0.8 }}
    />
  )
}

export default AnimatedBackground
