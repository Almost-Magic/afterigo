/**
 * Shamir's Secret Sharing Implementation
 *
 * This implements Shamir's Secret Sharing over GF(256) - the field of 256 elements.
 * This allows splitting a secret into n shares such that any k shares can reconstruct it,
 * but k-1 shares reveal ZERO information about the secret.
 *
 * Pure TypeScript implementation - no external dependencies.
 */

// GF(256) operations using polynomial arithmetic

// Generate the exponent-to-value and value-to-exponent lookup tables for GF(256)
// Using the primitive polynomial x^8 + x^4 + x^3 + x + 1 = 0x11B
const GF256_EXP: number[] = new Array(512)
const GF256_LOG: number[] = new Array(256)

function initGF256(): void {
  let x = 1
  for (let i = 0; i < 255; i++) {
    GF256_EXP[i] = x
    GF256_LOG[x] = i
    x <<= 1
    if (x & 0x100) {
      x ^= 0x11B
    }
  }
  for (let i = 255; i < 512; i++) {
    GF256_EXP[i] = GF256_EXP[i - 255]
  }
}

initGF256()

// Addition in GF(256) is just XOR
export function gfAdd(a: number, b: number): number {
  return a ^ b
}

// Subtraction in GF(256) is the same as addition (XOR)
export function gfSub(a: number, b: number): number {
  return a ^ b
}

// Multiplication in GF(256)
export function gfMul(a: number, b: number): number {
  if (a === 0 || b === 0) return 0
  const logSum = GF256_LOG[a] + GF256_LOG[b]
  return GF256_EXP[logSum % 255]
}

// Division in GF(256)
export function gfDiv(a: number, b: number): number {
  if (b === 0) throw new Error('Division by zero')
  if (a === 0) return 0
  const logDiff = GF256_LOG[a] - GF256_LOG[b]
  return GF256_EXP[logDiff % 255 + 255] // Ensure positive index
}

// Inverse in GF(256)
export function gfInv(a: number): number {
  if (a === 0) throw new Error('No inverse of zero')
  return GF256_EXP[255 - GF256_LOG[a]]
}

// Evaluate a polynomial at a point using Horner's method
function evaluatePolynomial(
  coefficients: number[],
  x: number
): number {
  let result = 0
  // Start from highest degree
  for (let i = coefficients.length - 1; i >= 0; i--) {
    result = gfAdd(gfMul(result, x), coefficients[i])
  }
  return result
}

// Generate random bytes for cryptographic security
function secureRandom(max: number): number {
  const range = max
  const bytesNeeded = Math.ceil(Math.log2(range) / 8)
  const maxValid = Math.pow(256, bytesNeeded) - 1
  const maxValidRounded = maxValid - ((maxValid + 1) % range)

  let randomValue: number
  const randomBytes = new Uint8Array(bytesNeeded)

  do {
    crypto.getRandomValues(randomBytes)
    randomValue = 0
    for (let i = 0; i < bytesNeeded; i++) {
      randomValue = randomValue * 256 + randomBytes[i]
    }
  } while (randomValue > maxValidRounded)

  return randomValue % range
}

// Generate a random non-zero element in GF(256)
function randomNonZero(): number {
  let result: number
  do {
    result = secureRandom(256)
  } while (result === 0)
  return result
}

/**
 * Split a secret into multiple shares using Shamir's Secret Sharing
 *
 * @param secret The secret as a Uint8Array
 * @param numShares Number of shares to create
 * @param threshold Minimum shares needed to reconstruct
 * @returns Array of shares as Uint8Arrays
 */
export function splitSecret(
  secret: Uint8Array,
  numShares: number,
  threshold: number
): Uint8Array[] {
  if (threshold < 2) {
    throw new Error('Threshold must be at least 2')
  }
  if (threshold > numShares) {
    throw new Error('Threshold cannot exceed number of shares')
  }
  if (numShares < 2 || numShares > 255) {
    throw new Error('Number of shares must be between 2 and 255')
  }

  // Create random coefficients for the polynomial
  // The secret becomes the constant term (a0)
  const coefficients: number[] = [secret[0]] // a0 = first byte of secret

  for (let i = 1; i < threshold; i++) {
    coefficients.push(randomNonZero())
  }

  // Generate shares for x = 1, 2, 3, ...
  const shares: Uint8Array[] = []

  for (let i = 1; i <= numShares; i++) {
    const share = new Uint8Array(secret.length + 1)
    share[0] = i // First byte is the x-coordinate (share index)

    // Evaluate polynomial at x = i for each byte of the secret
    // Each byte of the secret is the constant term of a separate polynomial
    for (let j = 0; j < secret.length; j++) {
      // Create a polynomial where:
      // - a0 = secret[j]
      // - a1 to a(threshold-1) = random coefficients
      const byteCoeffs: number[] = [secret[j]]
      for (let k = 1; k < threshold; k++) {
        // Use different random values for each byte to avoid patterns
        byteCoeffs.push(randomNonZero())
      }
      share[j + 1] = evaluatePolynomial(byteCoeffs, i)
    }

    shares.push(share)
  }

  return shares
}

/**
 * Reconstruct a secret from shares using Lagrange interpolation
 *
 * @param shares Array of shares (each is Uint8Array with format: [x, y0, y1, ...])
 * @param threshold Minimum shares needed (defaults to shares.length)
 * @returns The reconstructed secret as Uint8Array
 */
export function combineShares(
  shares: Uint8Array[],
  threshold?: number
): Uint8Array {
  if (shares.length < 2) {
    throw new Error('At least 2 shares are required')
  }

  const effectiveThreshold = threshold || shares.length
  if (shares.length < effectiveThreshold) {
    throw new Error(`At least ${effectiveThreshold} shares are required to reconstruct`)
  }

  const shareLength = shares[0].length
  const secretLength = shareLength - 1

  // Get the x-coordinates (first byte of each share)
  const xCoords = shares.map(share => share[0])

  // Reconstruct each byte of the secret separately
  const secret = new Uint8Array(secretLength)

  for (let byteIndex = 0; byteIndex < secretLength; byteIndex++) {
    // Collect the y-values for this byte from all shares
    const yValues = shares.map(share => share[byteIndex + 1])

    // Use the first 'threshold' shares for interpolation
    const usedX = xCoords.slice(0, effectiveThreshold)
    const usedY = yValues.slice(0, effectiveThreshold)

    // Lagrange interpolation at x = 0
    // f(0) = Σ(yi * li(0)) where li(0) = Π(xj / (xj - xi)) for j != i
    let reconstructedByte = 0

    for (let i = 0; i < effectiveThreshold; i++) {
      // Calculate Lagrange basis polynomial l_i(0)
      let numerator = 1
      let denominator = 1

      for (let j = 0; j < effectiveThreshold; j++) {
        if (i !== j) {
          numerator = gfMul(numerator, gfSub(0, usedX[j]))
          denominator = gfMul(denominator, gfSub(usedX[i], usedX[j]))
        }
      }

      const lagrangeCoeff = gfDiv(numerator, denominator)
      reconstructedByte = gfAdd(reconstructedByte, gfMul(usedY[i], lagrangeCoeff))
    }

    secret[byteIndex] = reconstructedByte
  }

  return secret
}

/**
 * Verify that a set of shares can reconstruct the original secret
 * This is useful for testing
 *
 * @param shares Array of shares
 * @param threshold Minimum shares needed
 * @returns The reconstructed secret
 */
export function verifyAndReconstruct(
  shares: Uint8Array[],
  threshold: number
): Uint8Array {
  if (shares.length < threshold) {
    throw new Error(`Need at least ${threshold} shares`)
  }

  return combineShares(shares, threshold)
}

/**
 * Convert shares to a shareable format (Base64)
 */
export function shareToBase64(share: Uint8Array): string {
  return arrayBufferToBase64(share.buffer)
}

/**
 * Convert from Base64 back to share format
 */
export function base64ToShare(base64: string): Uint8Array {
  const buffer = base64ToArrayBuffer(base64)
  return new Uint8Array(buffer)
}

// Helper: arrayBufferToBase64 (same as in encryption.ts)
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary)
}

// Helper: base64ToArrayBuffer (same as in encryption.ts)
function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binary = atob(base64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return bytes.buffer
}
