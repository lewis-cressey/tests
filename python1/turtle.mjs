class Vec2D {
    constructor(x, y) {
        this.x = x
        this.y = y
    }

    addVec2D(v) {
        return new Vec2D(this.x + v.x, this.y + v.y)
    }

    mul(s) {
        return new Vec2D(this.x * s, this.y * s)
    }

    rotate(degrees) {
        const radians = Math.PI * degrees / 180
        const sin = Math.sin(radians)
        const cos = Math.cos(radians)
        const x = this.x * cos - this.y * sin
        const y = this.x * sin + this.y * cos
        return new Vec2D(x, y)
    }
}

class Turtle {
    constructor(canvas) {
        this.canvas = canvas
        this.saveImage = undefined

        const size = 12
        this.points = [
            new Vec2D(0, size).rotate(150),
            new Vec2D(0, size * 0.7).rotate(180),
            new Vec2D(0, size).rotate(210),
        ]

        this.reset()

        window.setInterval(event => {
            this.render()
        }, 20)
    }

    getHistory() {
        const angles = []
        const lengths = []
        for (let angle of this.history.keys()) {
			angles.push(parseInt(angle))
            lengths.push(this.history.get(angle))
        }
        angles.sort((a, b) => {
			if (a > b) return 1
			if (a < b) return -1
			return 0
		})
        return { angles, lengths }
    }

    enqueueState() {
        this.stateQueue.push({
            position: this.position,
            bearing: this.bearing
        })
        return this
    }

    reset() {
        this.history = new Map()
        this.saveImage = undefined
		this.position = new Vec2D(0, 0)
		this.bearing = 0
        this.stateQueue = []
        this.enqueueState()
        const ctx = this.canvas.getContext("2d")
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
    }

	turn(degrees) {
		const newBearing = this.bearing + degrees
        return this.setBearing(newBearing)
	}

	setPos(x, y) {
		this.position = new Vec2D(x, y)
        return this
	}

    setBearing(newBearing) {
        let oldBearing = this.bearing
        newBearing = newBearing >= 0 ? newBearing % 360 : 360 - (-newBearing) % 360

        if (newBearing < oldBearing ) {
            const alt = 360 + newBearing
            if (alt - oldBearing < oldBearing - newBearing) {
                newBearing = alt
            }
        } else {
            const alt = 360 + oldBearing
            if (alt - newBearing < newBearing - oldBearing) {
                oldBearing = alt
            }
        }

        const step = 10 / Math.abs(newBearing - oldBearing)
        for (let scale = 0; scale < 1; scale += step) {
            this.bearing = newBearing * scale + oldBearing * (1 - scale)
            this.enqueueState()
        }

        this.bearing = newBearing % 360
        return this.enqueueState()
    }

	move(length) {
        const oldPosition = this.position
        const newPosition = new Vec2D(0, length).rotate(-this.bearing).addVec2D(oldPosition)

        const step = 4 / length
        for (let scale = 0; scale < 1; scale += step) {
            this.position = newPosition.mul(scale).addVec2D(oldPosition.mul(1 - scale))
            this.enqueueState()
        }

        this.position = newPosition

        const value = this.history.get(this.bearing) ?? 0
        this.history.set(this.bearing, value + length)
        return this.enqueueState()
	}

	render() {
        const queue = this.stateQueue
        const state0 = queue.length > 1 ? queue.shift() : queue[0]
        const state1 = queue[0]

        const ctx = this.canvas.getContext("2d")
        const cx = this.canvas.width / 2
        const cy = this.canvas.height / 2

        if (this.saveImage) {
            ctx.putImageData(this.saveImage, 0, 0)
        }

        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(cx + state0.position.x, cy - state0.position.y)
        ctx.lineTo(cx + state1.position.x, cy - state1.position.y)

        ctx.strokeStyle = "black"
        ctx.stroke()

        this.saveImage = ctx.getImageData(0, 0, this.canvas.width, this.canvas.height)

        ctx.beginPath()
        ctx.moveTo(cx + state1.position.x, cy - state1.position.y)

		for (let point of this.points) {
			point = point.rotate(-state1.bearing).addVec2D(state1.position)
            ctx.lineTo(cx + point.x, cy - point.y)
		}

        ctx.closePath()

        ctx.fillStyle = "black"
        ctx.fill()
        ctx.strokeStyle = "white"
        ctx.stroke()
	}
}

window.turtle = new Turtle(document.querySelector("#turtle-canvas"))
