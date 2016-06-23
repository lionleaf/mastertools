using UnityEngine;

public class NoiseBG : MonoBehaviour {

	private Texture2D noiseTexture;
	private Color[] pix;

	void Start() {
		noiseTexture = new Texture2D (1024, 1024);
		GetComponent<Renderer> ().material.mainTexture = noiseTexture;
		pix = new Color[noiseTexture.width * noiseTexture.height];
	}

	void Update () {
		if (Screenshotter.backgroundNeedsUpdate) {
			for (int y = 0; y < noiseTexture.height; y++) {
				for (int x = 0; x < noiseTexture.width; x++) {
					float sample = Random.value;
					pix [y * noiseTexture.width + x] = new Color (sample, sample, sample);
				}
			}
			noiseTexture.SetPixels (pix);
			noiseTexture.Apply ();
			Screenshotter.backgroundNeedsUpdate = false;
		}
	}
}
